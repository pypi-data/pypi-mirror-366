"""
File: querry_bunch_projects.py
Author: Antoine Laurent
Email: alaurent@agencemobilitedurable.ca
Github: https://github.com/alaurent34
Description:
"""

import itertools
import json
import os
import re
import unicodedata
import logging
from json import JSONDecodeError

import requests
from requests.compat import urljoin
import pandas as pd
import geopandas as gpd
from unidecode import unidecode

from lapin.constants import SEG_DB_ID, SEG_DB_SIDE, SEG_DB_STREET

CURBSNAPP_HOST = os.environ.get("CURBSNAPP_HOST", "")
CURBSNAPP_KEY = os.environ.get("CURBSNAPP_KEY", "")
API_FETCH = "api/fetchProjectData"
API_GEOBASE_SIMPLE = "api/fetchGeobase"
API_GEOBASE_DOUBLE = "api/fetchGeobaseDouble"
API_GEOBASE_VERS = "api/fetchFullGeobase"
API_GEO_DBL_VERS = "api/fetchFullGeobaseDouble"
API_CONNECT = "api/login"

GEOBASE_DBL_COL_DROP = ["REVERSE", "LENGTH", "NONPARCOURU", "MODIFIED"]


logger = logging.getLogger(__name__)


def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
        value = re.sub(r"[^\w\s-]", "", value.lower())

    return re.sub(r"[-\s]+", "-", value).strip("-_")


def connect(url, user: str, password: str) -> requests.Session:
    """_summary_

    Parameters
    ----------
    url : _type_
        _description_
    user : str
        _description_
    password : str
        _description_

    Returns
    -------
    requests.Session
        _description_
    """

    login_data = {"username": user, "password": password}

    session = requests.Session()
    session.post(url, data=login_data, timeout=600)

    return session


def generic_api_call(
    url: str,
    active_session: requests.Session | None = None,
    key: str | None = None,
    data: dict | None = None,
) -> dict[str, object]:
    """Generic POST api call

    Parameters
    ----------
    url : str
        URL of the API host
    active_session : requests.Session, optional
        The session is activated via cookies, by default None.
    key : str, optional
        Authentication is done by API key, by default None.
    data : dict, optional
        POST data to pass the API, default None.
    as_json : bool
        Return response as JSON dict.

    """

    if not data:
        data = {}
    if key:
        data["apiKey"] = key

    if active_session:
        result = active_session.post(url, json=data, timeout=600, verify=False)
    else:
        result = requests.post(url, json=data, timeout=600, verify=False)

    try:
        result = result.json()
    except JSONDecodeError:
        result.raise_for_status()
    else:
        return result


def project_api_call(
    project_name: str,
    url: str,
    active_session: requests.Session | None = None,
    key: str | None = None,
) -> dict:
    """
    doc
    """

    data = {"projectId": project_name}
    proj_data = generic_api_call(url, active_session, key, data)
    return proj_data


def merge_geobases(geobases_list: list[dict]) -> tuple[gpd.GeoDataFrame, list[str]]:
    """_summary_

    Parameters
    ----------
    geobases_list : list
        _description_

    Returns
    -------
    gpd.GeoDataFrame
        _description_
    """
    if all(not geobase for geobase in geobases_list):
        return (
            gpd.GeoDataFrame(
                columns=[SEG_DB_ID, SEG_DB_SIDE, SEG_DB_STREET, "geometry"],
                crs="epsg:4326",
            ),
            [],
        )

    # We concat the dict so that the data under the same key on every dict is place in a list.
    geobases_dict = {
        key: list(itertools.chain([d.get(key, []) for d in geobases_list]))
        for key in set().union(*geobases_list)
    }
    versions = geobases_dict.get("geobaseVersion", ["null"])
    geobases = [
        gpd.read_file(json.dumps(geobase)) for geobase in geobases_dict.get("data", [])
    ]
    return (gpd.GeoDataFrame(pd.concat(geobases)), versions)


def merge_capacities(capacities_list: list[dict[str, object]]) -> dict[str, object]:
    """TODO: Docstring for merge_capacities.

    :capacities_list: List of capacity objects
    :returns: TODO

    """
    return itertools.chain(*capacities_list)


def save_restrictions(project_name: str, capacity_array: dict):
    """TODO: Docstring for save_capacity.

    Parameters
    ----------
    project_name: str
        Name of the project

    """

    os.makedirs("./output/", exist_ok=True)

    with open(
        "output/" + slugify(unidecode(project_name)) + "_capacity_array.json",
        "w+",
        encoding="utf-8",
    ) as f:
        json.dump(capacity_array, f)


def get_geobase_versions(geobase_type: str = "simple") -> list[int]:

    if geobase_type not in ["simple", "double"]:
        raise ValueError("invalid geobase_type provided.")

    api_route = (
        f"/api/fetchGeobase{'Double' if geobase_type == 'double' else ''}Versions"
    )

    geo_versions = generic_api_call(
        urljoin(CURBSNAPP_HOST, api_route),
        None,
        CURBSNAPP_KEY,
        None,
    )

    available_verions = [v for p in geo_versions["data"] for _, v in p.items()]

    return available_verions


def get_geobase(
    version: str = "latest", geobase_type: str = "simple"
) -> tuple[gpd.GeoDataFrame, str]:
    """Get the geobase at version from Curbsnapp

    Parameters
    ----------
    version : str
        version number, by default 'latest'
    geobase_type : str
        Type of geobase to query, by default 'simple'

    Return
    ------
    geopandas.GeoDataFrame
        Geobase queried

    Raises
    ------
    ValueError
        geobase_type must be chosen from ['simple', 'double']
    ValueError
        No version specified

    """

    if geobase_type not in ["simple", "double"]:
        raise ValueError("invalid geobase_type provided.")

    api_route = (
        f"/api/fetchGeobase{'Double' if geobase_type == 'double' else ''}Versions"
    )

    if version is None:
        geo_versions = generic_api_call(
            urljoin(CURBSNAPP_HOST, api_route),
            None,
            CURBSNAPP_KEY,
            None,
            True,
        )

        available_verions = [v for p in geo_versions["data"] for _, v in p.items()]
        logger.error(
            "No version specified for the fetch. Available version are: %s",
            available_verions,
        )
        raise ValueError(
            f"No geobase version specified, available versions: {available_verions}"
        )

    if version == "latest":
        version_json = {}
    else:
        version_json = {"geobaseVersion": version}

    api_route = urljoin(CURBSNAPP_HOST, API_GEOBASE_VERS)
    if geobase_type == "double":
        api_route = urljoin(CURBSNAPP_HOST, API_GEO_DBL_VERS)

    geobase = generic_api_call(api_route, None, CURBSNAPP_KEY, version_json)
    version = geobase.get("geobaseVersion", "null")

    geobase = gpd.read_file(json.dumps(geobase["data"]))

    geobase.columns = [
        col.upper() if col != "geometry" else col for col in geobase.columns
    ]

    return geobase, version


def get_project_geobases(
    projects_list: list, geobase_type: str = "simple"
) -> tuple[gpd.GeoDataFrame, list[str]]:
    """_summary_

    Parameters
    ----------
    projects_list : list
        _description_
    geobase_type: str, optional
        Type of geobase to querry. Value can be
        'simple' or 'double', by default 'simple'.

    Returns
    -------
    gpd.GeoDataFrame
        Geobase

    Raises
    -----
    ValueError
    """

    if geobase_type not in ["simple", "double"]:
        raise ValueError("invalid geobase_type provided.")

    host = urljoin(CURBSNAPP_HOST, API_GEOBASE_SIMPLE)
    if geobase_type == "double":
        host = urljoin(CURBSNAPP_HOST, API_GEOBASE_DOUBLE)

    geobases = map(
        project_api_call,
        projects_list,
        itertools.repeat(host),
        itertools.repeat(None),
        itertools.repeat(CURBSNAPP_KEY),
    )
    geobase, versions = merge_geobases(list(geobases))

    geobase.columns = [
        col.upper() if col != "geometry" else col for col in geobase.columns
    ]

    # drop unwanted field
    geobase = geobase.drop(columns=GEOBASE_DBL_COL_DROP, errors="ignore")

    geobase = geobase.reset_index(drop=True)
    geobase = geobase.drop_duplicates()

    return gpd.GeoDataFrame(geobase), versions


def get_project_capacities(
    projects_list: list, user: str = None, pwd: str = None, output: list[str] = None
) -> dict:
    """_summary_

    Parameters
    ----------
    projects_list : list
        _description_
    user : str, optional
        _description_, by default None
    pwd : str, optional
        _description_, by default None
    output : list[str], optional
        _description_, by default None

    Returns
    -------
    dict
        _description_
    """
    if user and pwd:
        session = (
            connect(url=urljoin(CURBSNAPP_HOST, API_CONNECT), user=user, password=pwd)
            if user
            else None
        )

        capacities = map(
            project_api_call,
            projects_list,
            itertools.repeat(urljoin(CURBSNAPP_HOST, API_FETCH)),
            itertools.repeat(session),
        )
    else:
        capacities = map(
            project_api_call,
            projects_list,
            itertools.repeat(urljoin(CURBSNAPP_HOST, API_FETCH)),
            itertools.repeat(None),
            itertools.repeat(CURBSNAPP_KEY),
        )

    merge = len(projects_list) > 1

    # save
    if output:
        projects_list = output

    if merge:
        capacities = merge_capacities(list(capacities))
        capacities = [list(capacities)]
    else:
        capacities = list(capacities)

    list(map(save_restrictions, projects_list, capacities))

    capacities = capacities[0]

    return capacities
