import copy
import json
import re
import urllib.parse
from datetime import datetime, timedelta, timezone
from typing import List, cast

import azure
import azure.cosmos
import azure.cosmos.cosmos_client as cosmos_client
import geopandas as gpd
import numpy as np
import pandas as pd
from lapin.io.types import CosmosConfig, PostgresConfig

from sqlalchemy import JSON, Column, Engine, Integer, String, create_engine

from sqlalchemy.orm import declarative_base

Base = declarative_base()


class LapinConfigDB(Base):
    __tablename__ = "results"
    __table_args__ = {"schema": "lapin"}

    id = Column(Integer, primary_key=True, index=True)
    result_name = Column(String)
    result_type = Column(String)
    result_period = Column(String)
    json_result = Column(JSON)
    fk_runs_id = Column(Integer)
    fk_config_id = Column(Integer)


def presume_date(
    dataframe: pd.DataFrame | gpd.GeoDataFrame,
) -> pd.DataFrame | gpd.GeoDataFrame:
    """Set datetime by presuming any date values in the column
        indicates that the column data type should be datetime.

    Args:
        dataframe: Pandas dataframe.

    Returns:
        Pandas dataframe.

    Raises:
        None
    """
    df = dataframe.copy()
    mask = dataframe.astype(str).apply(
        lambda x: x.str.match(r"(\d{4}-\d{2}-\d{2})+").any()
    )
    df_dates = df.loc[:, mask].apply(pd.to_datetime, errors="coerce")
    for col in df_dates.columns:
        df[col] = df_dates[col]
    return df


def cosmos_result_to_json(cosmos_result: List[dict]) -> dict:
    """_summary_

    Parameters
    ----------
    cosmos_geom : list
        Result of a query to a geographic cosmos container

    Returns
    -------
    dict

    """
    # by default we add a crs
    geojson = {
        "type": "FeatureCollection",
        "crs": {
            "type": "name",
            "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"},
        },
        "features": cosmos_result,
    }

    return geojson


def get_postgres_engine(
    host: str, user: str, pwd: str, port: int, database: str
) -> Engine:

    user = urllib.parse.quote_plus(user)
    pwd = urllib.parse.quote_plus(pwd)
    engine = create_engine(
        f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{database}"
    )

    return engine


def parse_dates(
    dates: List[dict[str, str]], date_only: bool = True, to_string: bool = True
) -> List[dict[str, str]] | List[dict[str, datetime]]:
    """_summary_

    Parameters
    ----------
    dates : List[dict[str, str]]
        _description_
    date_only : bool, optional
        _description_, by default True

    Returns
    -------
    List[dict[str, str]]
        _description_
    """

    dates = copy.deepcopy(dates)

    for date in dates:
        from_d = datetime.fromisoformat(date["from"])
        to_d = datetime.fromisoformat(date["to"])

        from_d = from_d.astimezone()
        to_d = to_d.astimezone()
        to_d += timedelta(hours=23, minutes=59, seconds=59)

        if date_only:
            from_d_utc = from_d.astimezone(timezone.utc).date()
            to_d_utc = to_d.astimezone(timezone.utc).date()
            format_dt = "%Y-%m-%d"

        else:
            from_d_utc = from_d.astimezone(timezone.utc)
            to_d_utc = to_d.astimezone(timezone.utc)
            format_dt = "%Y-%m-%d %H:%M:%S"

        if to_string:
            date["from"] = from_d_utc.strftime(format_dt)
            date["to"] = to_d_utc.strftime(format_dt)
        else:
            date["from"] = from_d_utc
            date["to"] = to_d_utc

    return dates


def add_dates_to_query(
    query: str,
    dates: List[dict],
    date_col: str = "date",
) -> str:
    """
    Parameters
    ----------
    container: azure.cosmos.container.ContainerProxy
        Azure container to query
    dates: List[dict]
        List of date_range to query. Date range are dict with keys `from`,
        `to`
    query: str
        String query
    date_col: str, optional
        Date column for the container, by default 'date'

    Returns
    -------
    str
        Query enhance with a filter on date_col
    """

    if re.search("where", query, re.IGNORECASE):
        query += " AND "
    else:
        query += " WHERE "

    dates = parse_dates(dates, True, True)

    where_cond = " ("
    for date in dates:
        where_cond += (
            f"{date_col} >= '{date['from']}'" + f" AND {date_col} <= '{date['to']}'"
        )
        where_cond += " OR "

    where_cond += " 1=2)"

    query += where_cond

    return query


def query_engine(engine: Engine, query: str, **kwargs) -> pd.DataFrame:
    if kwargs and kwargs.get("dates"):
        if kwargs.get("dates") and not kwargs.get("date_col"):
            raise ValueError("date_col sould be set for date query.")
        query = add_dates_to_query(query, kwargs.pop("dates"), kwargs.pop("date_col"))

    df = pd.read_sql(sql=query, con=engine, **kwargs)

    return df


def query_container(
    container: azure.cosmos.container.ContainerProxy,
    query: str,
    enable_cross_partition_query=False,
    **kwargs,
) -> List[dict]:
    """_summary_

    Parameters
    ----------
    container : azure.cosmos.container.ContainerProxy
        _description_
    query : str
        _description_
    cross_partitions : bool, optional
        _description_, by default False

    Returns
    -------
    _type_
        _description_
    """
    if kwargs.get("dates", None):
        query = add_dates_to_query(query, kwargs.get("dates"), kwargs.get("date_col"))
    # querry

    res_query = container.query_items(
        query=query, enable_cross_partition_query=enable_cross_partition_query
    )

    return list(res_query)


def cosmos_list_to_frame(
    query_result: list[dict], filter_dates: List[dict[str, str]] | None = None
) -> pd.DataFrame | gpd.GeoDataFrame:

    data = cosmos_result_to_json(query_result)
    try:
        data = gpd.read_file(json.dumps(data))
    except ValueError:
        data = pd.read_json(json.dumps(data))

    if filter_dates and not data.empty:
        dates = parse_dates(filter_dates, False, False)
        # convert all datetime like columns to datetime type
        data = presume_date(data)
        # get the first datetime64 column in the frame
        try:
            dt_col = data.select_dtypes(include="datetime64").columns[0]
        except IndexError:
            dt_col = data.select_dtypes(include="datetimetz").columns[0]
        except IndexError:
            raise ValueError("Datetime column not found in data.")

        data[dt_col] = pd.to_datetime(data[dt_col], format="ISO8601", utc=True)
        mask = np.full(data.shape[0], False, dtype=bool)
        for date in dates:
            mask = mask | (
                (data[dt_col] >= date["from"]) & (data[dt_col] <= date["to"])
            )
        data = data.loc[mask].copy()

    return data


def get_cosmos_engine(cosmos_config) -> azure.cosmos.container.ContainerProxy:
    host = cosmos_config["host"]
    master_key = cosmos_config["master_key"]
    database_id = cosmos_config["database_id"]
    container_id = cosmos_config["container_id"]

    client = cosmos_client.CosmosClient(
        host,
        {"masterKey": master_key},
        user_agent="CosmosDBPythonQuickstart",
        user_agent_overwrite=True,
    )

    # setup database for this sample
    db = client.get_database_client(database_id)
    container = db.get_container_client(container_id)

    return container


def get_engine(engine_type: str, engine_conf: CosmosConfig | PostgresConfig) -> ...:
    if engine_type == "cosmos-db":
        engine_conf = cast(CosmosConfig, engine_conf)
        return get_cosmos_engine(engine_conf)
    if engine_type == "postgresql":
        engine_conf = cast(PostgresConfig, engine_conf)
        return get_postgres_engine(**engine_conf)
    else:
        raise ValueError(f"Engine type {engine_type} not supported")
    # if engine_type == "curbsnapp":
    #     engine_conf = cast(CurbsnappConfig, engine_conf)
    #     return get_geobase(**engine_conf)
