import copy
import re
from datetime import datetime, timedelta, timezone
from typing import List


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
            f"c.{date_col} >= \"{date['from']}\""
            + f" AND c.{date_col} <= \"{date['to']}\""
        )
        where_cond += " OR "

    where_cond += " 1=2)"

    query += where_cond

    return query
