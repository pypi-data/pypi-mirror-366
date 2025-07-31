# Copyright 2024 CS Group
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""FastAPI application using PGStac.

Enables the extensions specified as a comma-delimited list in
the ENABLED_EXTENSIONS environment variable (e.g. `transactions,sort,query`).
If the variable is not set, enables all extensions.
"""
import asyncio
import os
import sys
from contextlib import asynccontextmanager
from http import HTTPStatus
from os import environ as env
from typing import Annotated

import httpx
from brotli_asgi import BrotliMiddleware
from fastapi import Depends, FastAPI, HTTPException, Request, Security
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse, ORJSONResponse
from fastapi.routing import APIRoute
from httpx._config import DEFAULT_TIMEOUT_CONFIG
from rs_server_catalog import __version__
from rs_server_catalog.data_lifecycle import DataLifecycle
from rs_server_catalog.user_catalog import UserCatalog
from rs_server_common import settings as common_settings
from rs_server_common.authentication.apikey import (
    APIKEY_AUTH_HEADER,
    APIKEY_SCHEME_NAME,
)
from rs_server_common.middlewares import (
    AuthenticationMiddleware,
    HandleExceptionsMiddleware,
    apply_middlewares,
)
from rs_server_common.settings import env_bool
from rs_server_common.utils import init_opentelemetry
from rs_server_common.utils.logging import Logging
from stac_fastapi.api.app import StacApi
from stac_fastapi.api.errors import ErrorResponse
from stac_fastapi.api.middleware import CORSMiddleware, ProxyHeaderMiddleware
from stac_fastapi.api.models import (
    ItemCollectionUri,
    create_get_request_model,
    create_post_request_model,
    create_request_model,
)
from stac_fastapi.extensions.core import (  # pylint: disable=no-name-in-module
    FieldsExtension,
    FilterExtension,
    SortExtension,
    TokenPaginationExtension,
    TransactionExtension,
)
from stac_fastapi.extensions.third_party import BulkTransactionExtension
from stac_fastapi.pgstac.config import Settings
from stac_fastapi.pgstac.core import CoreCrudClient
from stac_fastapi.pgstac.db import close_db_connection, connect_to_db
from stac_fastapi.pgstac.extensions import QueryExtension
from stac_fastapi.pgstac.extensions.filter import FiltersClient
from stac_fastapi.pgstac.transactions import BulkTransactionsClient, TransactionsClient
from stac_fastapi.pgstac.types.search import PgstacSearch
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.routing import Route

logger = Logging.default(__name__)

# Technical endpoints (no authentication)
TECH_ENDPOINTS = ["/_mgmt/ping"]


def must_be_authenticated(route_path: str) -> bool:
    """Return true if a user must be authenticated to use this endpoint route path."""

    # Remove the /catalog prefix, if any
    path = route_path.removeprefix("/catalog")

    no_auth = (path in TECH_ENDPOINTS) or (path in ["/api", "/api.html", "/health"]) or path.startswith("/auth/")
    return not no_auth


def add_parameter_owner_id(parameters: list[dict]) -> list[dict]:
    """Add the owner id dictionnary to the parameter list.

    Args:
        parameters (list[dict]): the parameters list
        where we want to add the owner id parameter.

    Returns:
        dict: the new parameters list with the owner id parameter.
    """
    description = "Catalog owner id"
    to_add = {
        "description": description,
        "required": False,
        "schema": {"type": "string", "title": description, "description": description},
        "name": "owner_id",
        "in": "path",
    }
    parameters.append(to_add)
    return parameters


def get_new_key(original_key: str) -> str:  # pylint: disable=missing-function-docstring
    """For all existing endpoints, add prefix and owner_id parameter."""
    res = ""
    match original_key:
        case "/":
            res = "/catalog/"
        case "/collections":
            res = "/catalog/collections"
        case "/collections/{collection_id}":
            res = "/catalog/collections/{owner_id}:{collection_id}"
        case "/collections/{collection_id}/items":
            res = "/catalog/collections/{owner_id}:{collection_id}/items"
        case "/collections/{collection_id}/items/{item_id}":
            res = "/catalog/collections/{owner_id}:{collection_id}/items/{item_id}"
        case "/search":
            res = "/catalog/search"
        case "/queryables":
            res = "/catalog/queryables"
        case "/collections/{collection_id}/queryables":
            res = "/catalog/collections/{owner_id}:{collection_id}/queryables"
        case "/collections/{collection_id}/bulk_items":
            res = "/catalog/collections/{owner_id}:{collection_id}/bulk_items"
        case "/conformance":
            res = "/catalog/conformance"
    return res


def extract_openapi_specification():  # pylint: disable=too-many-locals
    """Extract the openapi specifications and modify the content to be conform
    to the rs catalog specifications. Then, apply the changes in the application.
    """
    if app.openapi_schema:
        return app.openapi_schema
    openapi_spec = get_openapi(
        title=app.title,
        version=__version__,
        openapi_version=app.openapi_version,
        description=app.description,
        routes=app.routes,
    )
    # add starlette routes: /api, /api.html and /docs/oauth2-redirect and add /catalog prefix
    for route in app.routes:  # pylint: disable=redefined-outer-name
        if isinstance(route, Route) and route.path in ["/api", "/api.html", "/docs/oauth2-redirect"]:
            path = f"/catalog{route.path}"
            method = "GET"
            to_add = {
                "summary": f"Auto-generated {method} for {path}",
                "responses": {
                    "200": {
                        "description": "Successful Response",
                        "content": {"application/json": {"example": {"message": "Success"}}},
                    },
                },
                "operationId": "/catalog" + route.operation_id if hasattr(route, "operation_id") else route.path,
            }
            if common_settings.CLUSTER_MODE and must_be_authenticated(route.path):
                to_add["security"] = [{APIKEY_SCHEME_NAME: []}]
            openapi_spec["paths"].setdefault(path, {})[method.lower()] = to_add

    openapi_spec_paths = openapi_spec["paths"]
    for key in list(openapi_spec_paths.keys()):
        if key in TECH_ENDPOINTS:
            del openapi_spec_paths[key]
            continue

        new_key = get_new_key(key)
        if new_key:
            openapi_spec_paths[new_key] = openapi_spec_paths.pop(key)
            endpoint = openapi_spec_paths[new_key]
            for method_key in endpoint.keys():
                method = endpoint[method_key]
                if isinstance(method, dict):
                    if (  # Add the parameter owner_id in the endpoint if needed.
                        new_key not in ["/catalog/search", "/catalog/", "/catalog/collections"]
                        and "parameters" in method
                    ):
                        method["parameters"] = add_parameter_owner_id(method.get("parameters", []))
                    elif (  # Add description to the /catalog/search endpoint.
                        "operationId" in method
                        and isinstance(method["operationId"], str)
                        and method["operationId"] == "Search_search_get"
                    ):
                        method["description"] = (
                            "Endpoint /catalog/search. The filter-lang parameter is cql2-text by default."
                        )

    # Add all previous created endpoints.
    app.openapi_schema = openapi_spec
    return app.openapi_schema


settings = Settings()
extensions_map = {
    "transaction": TransactionExtension(
        client=TransactionsClient(),
        settings=settings,
        response_class=ORJSONResponse,
    ),
    "query": QueryExtension(),
    "sort": SortExtension(),
    "fields": FieldsExtension(),
    "pagination": TokenPaginationExtension(),
    "filter": FilterExtension(client=FiltersClient()),
    "bulk_transactions": BulkTransactionExtension(client=BulkTransactionsClient()),
}

if enabled_extensions := os.getenv("ENABLED_EXTENSIONS"):
    extensions = [extensions_map[extension_name] for extension_name in enabled_extensions.split(",")]
else:
    extensions = list(extensions_map.values())

post_request_model = create_post_request_model(extensions, base_model=PgstacSearch)
core_crud_client = CoreCrudClient(pgstac_search_model=post_request_model)


class UserCatalogMiddleware(BaseHTTPMiddleware):  # pylint: disable=too-few-public-methods
    """The user catalog middleware."""

    async def dispatch(self, request, call_next):
        """Redirect the user catalog specific endpoint and adapt the response content."""
        try:
            response = await UserCatalog(core_crud_client).dispatch(request, call_next)
            return response
        except (HTTPException, StarletteHTTPException) as exc:
            phrase = HTTPStatus(exc.status_code).phrase
            code = "".join(word.title() for word in phrase.split())
            return JSONResponse(
                status_code=exc.status_code,
                content=ErrorResponse(code=code, description=str(exc.detail)),
            )


items_get_request_model = create_request_model(
    "ItemCollectionURI",
    base_model=ItemCollectionUri,
    mixins=[TokenPaginationExtension().GET],
)

api = StacApi(
    settings=settings,
    extensions=extensions,
    items_get_request_model=items_get_request_model,
    client=core_crud_client,
    response_class=ORJSONResponse,
    search_get_request_model=create_get_request_model(extensions),
    search_post_request_model=post_request_model,
    middlewares=[
        Middleware(UserCatalogMiddleware),
        Middleware(BrotliMiddleware),
        Middleware(ProxyHeaderMiddleware),
        Middleware(AuthenticationMiddleware, must_be_authenticated=must_be_authenticated),
        Middleware(HandleExceptionsMiddleware),
        Middleware(
            CORSMiddleware,  # WARNING: must be last !
            allow_origins=common_settings.STAC_BROWSER_URLS,
            allow_methods=["*"],
            allow_headers=["*"],
            allow_credentials=True,
        ),
    ],
)
app = api.app
app.openapi = extract_openapi_specification

# In cluster mode, add the oauth2 authentication
if common_settings.CLUSTER_MODE:
    app = apply_middlewares(app)


# Data lifecycle management instance (cleaning of old assets)
lifecycle = DataLifecycle(app, core_crud_client)


@asynccontextmanager
async def lifespan(my_app: FastAPI):
    """The lifespan function."""
    try:
        # Connect to the databse
        db_info = f"'{env['POSTGRES_USER']}@{env['POSTGRES_HOST']}:{env['POSTGRES_PORT']}'"
        while True:
            try:
                await connect_to_db(my_app)
                logger.info("Reached %r database on %s", env["POSTGRES_DB"], db_info)
                break
            except ConnectionRefusedError:
                logger.warning("Trying to reach %r database on %s", env["POSTGRES_DB"], db_info)

                # timeout gestion if specified
                if my_app.state.pg_timeout is not None:
                    my_app.state.pg_timeout -= my_app.state.pg_pause
                    if my_app.state.pg_timeout < 0:
                        sys.exit("Unable to start up catalog service")
                await asyncio.sleep(my_app.state.pg_pause)

        common_settings.set_http_client(httpx.AsyncClient(timeout=DEFAULT_TIMEOUT_CONFIG))

        # Run the data lifecycle management as an automatic periodic task
        lifecycle.run()

        yield

    finally:
        await lifecycle.cancel()
        await close_db_connection(my_app)
        await common_settings.del_http_client()


app.router.lifespan_context = lifespan

# Configure OpenTelemetry
init_opentelemetry.init_traces(app, "rs.server.catalog")

# In local mode only or from the pytests, add an endpoint to manual trigger the data lifecycle management (for testing)
if common_settings.LOCAL_MODE or env_bool("FROM_PYTEST", default=False):

    @app.router.get("/data/lifecycle", include_in_schema=False)
    async def data_lifecycle(request: Request):
        """Trigger the data lifecycle management"""
        await lifecycle.periodic_once(request)


# In cluster mode, we add a FastAPI dependency to every authenticated endpoint so the lock icon (to enter an API key)
# can appear in the Swagger. This won't do the actual authentication, which is done by a FastAPI middleware.
# We do this because, in FastAPI, the dependencies are run after the middlewares, but here we need the
# authentication to work from inside the middlewares.
if common_settings.CLUSTER_MODE:

    async def just_for_the_lock_icon(
        apikey_value: Annotated[str, Security(APIKEY_AUTH_HEADER)] = "",  # pylint: disable=unused-argument
    ):
        """Dummy function to add a lock icon in Swagger to enter an API key."""

    # One scope for each Router path and method
    scopes = []
    for route in api.app.router.routes:
        if not isinstance(route, APIRoute) or not must_be_authenticated(route.path):
            continue
        for method_ in route.methods:
            scopes.append({"path": route.path, "method": method_})

    api.add_route_dependencies(scopes=scopes, dependencies=[Depends(just_for_the_lock_icon)])

# Pause and timeout to connect to database (hardcoded for now)
app.state.pg_pause = 3  # seconds
app.state.pg_timeout = 30


def run():
    """Run app from command line using uvicorn if available."""
    try:
        import uvicorn  # pylint: disable=import-outside-toplevel

        uvicorn.run(
            "rs_server_catalog.main:app",
            host=settings.app_host,
            port=settings.app_port,
            log_level="info",
            reload=settings.reload,
            root_path=os.getenv("UVICORN_ROOT_PATH", ""),
        )
    except ImportError:
        raise RuntimeError("Uvicorn must be installed in order to use command")  # pylint: disable=raise-missing-from


if __name__ == "__main__":
    run()
