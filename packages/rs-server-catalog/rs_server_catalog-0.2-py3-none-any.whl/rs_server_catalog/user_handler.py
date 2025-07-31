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
# pylint: disable=too-many-return-statements
"""This library contains all functions needed for the fastAPI middleware."""

import getpass
import os
import re
from typing import Any

from rs_server_common.authentication.oauth2 import AUTH_PREFIX
from starlette.requests import Request

CATALOG_OWNER_ID_STAC_ENDPOINT_REGEX = (
    r"/catalog/collections"
    r"(((?P<owner_collection_id>/.+?(?=/|$)))?"
    r"(?P<items>/.+?(?=/|$))?"
    r"(?P<item_id>/.+?(?=/|$))?)?"
)

# Regexp for catalog endpoints
COLLECTIONS_QUERYABLES_REGEX = r"/catalog/collections/((?P<owner_id>.+):)?(?P<collection_id>.+)/queryables"
BULK_ITEMS_REGEX = r"/catalog/collections/((?P<owner_id>.+):)?(?P<collection_id>.+)/bulk_items"
CATALOG_COLLECTION = "/catalog/collections"
CATALOG_PREFIX = "/catalog"

# Regexp for search endpoints
CATALOG_SEARCH = "/catalog/search"
CATALOG_SEARCH_QUERY_PARAMS = r"/catalog/search\?((?P<owner_id>.+):)?(?P<collection_id>.+)"  # noqa: W605


def get_user(endpoint_user: str | None, apikey_user: str | None):
    """Retrieve the user identifier based on provided parameters. Default is the
    current running user (used for local mode in general)

    Args:
        endpoint_user (str): User identifier from the endpoint.
        apikey_user (str): User identifier from the API key.

    Returns:
        str: The user identifier.
    """
    if endpoint_user:
        return endpoint_user
    if apikey_user:
        return apikey_user
    return os.getenv("RSPY_HOST_USER", default=getpass.getuser())


def reroute_url(  # type: ignore # pylint: disable=too-many-branches,too-many-statements
    request: Request,
    ids_dict: dict[str, Any],
):
    """Remove the prefix from the RS Server Frontend endpoints to get the
    RS Server backend catalog endpoints.

    Args:
        request (Request): The client request
        ids_dict (str): Dictionary to easily access important data of our request

    Raises:
        ValueError: If the path is not valid.

    Returns:
        str: Return the URL path with prefix removed.
        dict: Return a dictionary containing owner, collection and item ID.
    """
    path = request.url.path
    method = request.method
    patterns = [r"/_mgmt/ping", r"/api", r"/favicon.ico", "/data/lifecycle"]

    # Catch one endpoint of the following list
    regexp_list = [
        "/",
        "/catalog",
        "/catalog/",
        "/catalog/search",
        "/catalog/queryables",
        "/catalog/api",
        "/catalog/api.html",
        "/catalog/docs/oauth2-redirect",
        "/catalog/conformance",
    ]
    is_in_regexp_list = False
    for pattern in regexp_list:
        if re.fullmatch(pattern, path):
            path = path.replace(CATALOG_PREFIX, "") or "/"
            is_in_regexp_list = True
            break
    if is_in_regexp_list:
        # Don't validate other conditions if we alredy matched the previous regexps
        pass

    # Catch authentication endpoints (path should be left as it is in this case)
    elif path.startswith(f"{AUTH_PREFIX}/"):
        pass

    # Catch health endpoints
    elif "/health" in path:
        path = "/health"

    # The endpoint PUT "/catalog/collections" does not exists.
    elif path.rstrip("/") == CATALOG_COLLECTION and method != "PUT":
        path = "/collections"

    # Catch endpoint /catalog/collections/[{owner_id}:]{collection_id}/bulk_items
    elif match := re.fullmatch(BULK_ITEMS_REGEX, path):
        groups = match.groupdict()
        ids_dict["owner_id"] = get_user(groups["owner_id"], ids_dict["user_login"])
        ids_dict["collection_ids"].append(groups["collection_id"])
        path = f"/collections/{ids_dict['owner_id']}_{ids_dict['collection_ids'][0]}/bulk_items"

    # Catch endpoint /catalog/collections/[{owner_id}:]{collection_id}/queryables
    elif match := re.fullmatch(COLLECTIONS_QUERYABLES_REGEX, path):
        groups = match.groupdict()
        ids_dict["owner_id"] = get_user(groups["owner_id"], ids_dict["user_login"])
        ids_dict["collection_ids"].append(groups["collection_id"])
        path = f"/collections/{ids_dict['owner_id']}_{ids_dict['collection_ids'][0]}/queryables"

    # Catch all other endpoints.
    elif match := re.match(CATALOG_OWNER_ID_STAC_ENDPOINT_REGEX, path):
        groups = match.groupdict()
        if groups["owner_collection_id"]:
            # protection for more than one : (example-> /catalog/collections/ownerId:collection:Id/items)
            # the list owner_collection_id_split has one or at most two members (note the maxsplit = 1)
            owner_collection_id_split = groups["owner_collection_id"].lstrip("/").split(":", 1)
            if len(owner_collection_id_split) == 1:
                # the following handles the absence of the ownerId param, for endpoints like:
                # /catalog/collections/collectionId/items
                ids_dict["owner_id"] = get_user(None, ids_dict["user_login"])
                ids_dict["collection_ids"].append(owner_collection_id_split[0])
            else:
                # the following handles the presence of the ownerId param, for endpoints like:
                # /catalog/collections/ownerId:collectionId/items
                ids_dict["owner_id"] = owner_collection_id_split[0]
                ids_dict["collection_ids"].append(owner_collection_id_split[1])

        # /catalog/collections/{owner_id}:{collection_id}
        # case is the same for PUT / POST / DELETE, but needs different paths
        if groups["items"] is None and method != "DELETE":
            path = f"/collections/{ids_dict['owner_id']}_{ids_dict['collection_ids'][0]}"
        else:
            ids_dict["item_id"] = groups["item_id"]
            if ids_dict["item_id"] is None:
                if "items" in path:
                    path = f"/collections/{ids_dict['owner_id']}_{ids_dict['collection_ids'][0]}/items"
                else:
                    path = f"/collections/{ids_dict['owner_id']}_{ids_dict['collection_ids'][0]}"
            else:
                ids_dict["item_id"] = ids_dict["item_id"][1:]
                path = (
                    f"/collections/{ids_dict['owner_id']}_{ids_dict['collection_ids'][0]}/items/{ids_dict['item_id']}"
                )

    elif not any(re.fullmatch(pattern, path) for pattern in patterns):
        path = ""
    # Finally, update the path of the request with the new route
    request.scope["path"] = path


def add_user_prefix(  # pylint: disable=too-many-return-statements
    path: str,
    user: str | None,
    collection_id: str | None,
    feature_id: str = "",
) -> str:
    """
    Modify the RS server backend catalog endpoint to get the RS server frontend endpoint

    Args:
        path (str): RS server backend endpoint.
        user (str): The user ID.
        collection_id (str): The collection id.
        feature_id (str): The feature id.

    Returns:
        str: The RS server frontend endpoint.
    """
    new_path = path

    if path == "/collections":
        new_path = CATALOG_COLLECTION

    elif path == "/search":
        new_path = CATALOG_SEARCH

    elif user and (path == "/"):
        new_path = "/catalog/"

    elif user and collection_id and (path == f"/collections/{user}_{collection_id}"):
        new_path = f"/catalog/collections/{user}:{collection_id}"

    elif user and collection_id and (path == f"/collections/{user}_{collection_id}/items"):
        new_path = f"/catalog/collections/{user}:{collection_id}/items"

    elif user and collection_id and (path == f"/collections/{user}_{collection_id}/queryables"):
        new_path = f"/catalog/collections/{user}:{collection_id}/queryables"

    elif (
        user
        and collection_id
        and (f"/collections/{user}_{collection_id}/items" in path or f"/collections/{collection_id}/items" in path)
    ):  # /catalog/.../items/item_id
        new_path = f"/catalog/collections/{user}:{collection_id}/items/{feature_id}"

    return new_path


def remove_user_from_feature(feature: dict, user: str) -> dict:
    """Remove the user ID from the collection name in the feature.

    Args:
        feature (dict): a geojson that contains georeferenced
        data and metadata like the collection name.
        user (str): The user ID.

    Returns:
        dict: the feature with a new collection name without the user ID.
    """
    if user in feature["collection"]:
        feature["collection"] = feature["collection"].removeprefix(f"{user}_")
    return feature


def remove_user_from_collection(collection: dict, user: str) -> dict:
    """Remove the user ID from the id section in the collection.

    Args:
        collection (dict): A dictionary that contains metadata
        about the collection content like the id of the collection.
        user (str): The user ID.

    Returns:
        dict: The collection without the user ID in the id section.
    """
    if user and (user in collection.get("id", "")):
        collection["id"] = collection["id"].removeprefix(f"{user}_")
    return collection


def filter_collections(collections: list[dict], user: str) -> list[dict]:
    """filter the collections according to the user ID.

    Args:
        collections (list[dict]): The list of collections available.
        user (str): The user ID.

    Returns:
        list[dict]: The list of collections corresponding to the user ID
    """
    return [collection for collection in collections if user in collection["id"]]
