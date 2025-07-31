# -*- coding: utf-8 -*-
"""
Created on Wed Jun  9 10:12:56 2021

@author: lgauthier
@author: alaurent
"""
import re
import copy
import datetime
from deprecated import deprecated
import numpy as np
import pandas as pd
import geopandas as gpd
from statsmodels.stats.weightstats import DescrStatsW

from lapin import constants
from lapin.tools.ctime import Ctime
from lapin.tools.utils import (
    IncompleteDataError,
    restriction_aggfunc,
    enforce_restrictions,
    expand_network,
)
from lapin.tools.strings import is_numeric_transformable
from lapin.models.utils import slice_data_by_hour
from lapin.core.restrictions import Curbs
from lapin.core._utils import prepare_data_before_export


def get_hour_multiplier(freq: str) -> int:
    """Return the multiplier to go from freq unit to hours.

    Parameters
    ----------
    freq: str
        Unit of time. Must be in {'h', 'H', 'T', 'min', 'S', 'L',
        'ms', 'U', 'us', 'ns'}.

    Returns
    ------
    int

    Raise
    -----
    AttributeError
    """
    if freq == "H" or freq == "h":
        return 1
    elif freq in ["T", "min"]:
        return 60
    elif freq == "S":
        return 3600
    elif freq in ["L", "ms"]:
        return 3600000
    elif freq in ["U", "us"]:
        return 3600000000
    elif freq == "ns":
        return 3600000000000
    else:
        raise AttributeError(
            freq,
            "Should be one of the following : "
            + "{'h', 'H', 'T', 'min', 'S', 'L', 'ms', 'U', 'us', 'ns'}",
        )


def is_day_factor(freq: str) -> bool:
    """Is frequency a factor of one day

    Parameters
    ----------
    freq: str
        Frequency strings. Can have multiples, e.g. '5H'. See
        [here](https://pandas.pydata.org/docs/user_guide/timeseries.html#timeseries-offset-aliases)
        for a list of frequency aliases.

    Returns
    ------
    bool
    """
    # freq is smaller than a day
    time_match = re.search(r"(\d*)([HhTSLUN]|min|ms|us)", freq)
    if time_match:
        time = int(time_match.groups()[0]) if time_match.group()[0] else 1
        mult = time_match.groups()[1]
        if 24 * get_hour_multiplier(mult) % time == 0:
            return True
        return False
    # if freq is greater than a day it will have no consequences
    # to the calculus
    return True


def create_ununiform_bins(
    start: datetime.datetime, end: datetime.datetime, freq: str
) -> pd.DatetimeIndex:
    """Create bins that contains for each day in the interval provided by
    start and freq.  This does not generate equals range of bins.

    Parameters
    ----------
    start: datetime-like
        Left bound for generating dates.
    end: datetime-like
        Right bound for generating dates.
    freq: str
        Frequency strings. Can have multiples, e.g. ‘5H’. See
        [here](https://pandas.pydata.org/docs/user_guide/timeseries.html#timeseries-offset-aliases)
        for a list of frequency aliases.

    Returns
    -------
    pd.DateTimeIndex
    """
    freq = pd.Timedelta(freq)
    day_delta = datetime.timedelta(days=1, hours=0, minutes=0, seconds=0)
    cursor = copy.deepcopy(start)

    if start > end:
        raise ValueError("datetime end cannot be supperior that start")

    date_bins = []
    while cursor < end:
        date_bins.append(cursor)

        if (cursor + freq).date() > cursor.date():
            cursor = (
                cursor.replace(
                    hour=start.hour, minute=start.minute, second=start.second
                )
                + day_delta
            )
        else:
            cursor += freq

    # last bin
    date_bins.append(cursor)

    date_bins = [t.replace(tzinfo=None) for t in date_bins]
    if start.tzinfo:
        return pd.DatetimeIndex(date_bins).tz_localize(start.tzinfo)
    return pd.DatetimeIndex(date_bins)


def lapin_date_range(
    start: datetime.datetime, end: datetime.datetime, freq: str, **kwargs
) -> pd.DatetimeIndex:
    """Create date range that contains, for each day, the interval provided
    by start and freq. This does not generate equals range of bins if freq
    is not a factor of a day.

    Parameters
    ----------
    start: datetime-like
        Left bound for generating dates.
    end: datetime-like
        Right bound for generating dates.
    freq: str
        Frequency strings. Can have multiples, e.g. '5H'. See
        [here](https://pandas.pydata.org/docs/user_guide/timeseries.html#timeseries-offset-aliases)
        for a list of frequency aliases.
    **kwarg:
        pandas.date_range kwargs

    Returns
    -------
    pandas.DatetimeIndex

    See Also
    --------
    pandas.date_range
    """
    freq = copy.deepcopy(freq)
    # We can use pandas date_range if freq is a factor of a day
    if is_day_factor(freq):
        return pd.date_range(start=start, end=end, freq=freq, **kwargs)

    return create_ununiform_bins(start, end, freq)


def _occup_pivot_handle(
    occ_df: pd.DataFrame, pivot_col: str, weight: str, index: list[str]
) -> pd.DataFrame:
    """Aggregate the occupation at the segment and side of street level. The
    aggregation is parametred by attribute pivot_col. Default is aggregated
    value is occupancy. In addition, restrictions are applied even if no data
    is recolted by the LAPI vehicule.

    Paramaters
    ----------
    occ_df : pandas.DataFrame
        Unagregated occupancy computed for each segment on each lap of a LAPI
        vehicule.
    geodbl : geopandas.GeoDataFrame
        Geographical data of roads side of street.
    restrictionHandler : analysis.restrictions.RestrictionHandler
        An instance of the restriction engine for this LAPI data.
    pivot_col : string (Default: 'occ')
        Column values that will be aggregated.

    Returns
    -------
    aggregated_data : geopandas.GeoDataFrame
       Data aggregated at side of street level with restrictions when it
       applies.
    """

    # pivot this to have a column per hour
    occ_h = occ_df.pivot_table(
        pivot_col,
        index=index,
        aggfunc=lambda x: (
            DescrStatsW(
                data=x.to_list(), weights=occ_df.loc[x.index, weight].to_list()
            ).mean
            if occ_df.loc[x.index, weight].sum() > 0
            else 0
        ),
        columns="time",
        dropna=False,
    )
    occ_h = occ_h.rename_axis(None, axis=1)
    occ_h = occ_h.loc[~occ_h.isna().all(axis=1)].reset_index()

    return occ_h


def associate_time_freq(
    data: pd.DataFrame,
    days: str = "lun-dim",
    timeslot_beg: str = "0h00",
    timeslot_end: str = "23h59",
    freq: str = "30min",
) -> pd.DataFrame:
    """Create a columns time with time cut at freqence freq.

    Parameters
    ----------
    data : pandas.DataFrame
        Data with column 'time'
    timeslot_beg : str, optional
        Starting hour for compiling occupancy, by default '0h00'.
    timeslot_end : str, optional
        Stoping hour for compiling occupancy, by default '23h59'.
    freq : str or DateOffset, optional
        Frequency strings can have multiples, e.g. '1h'. See here for a list of
        frequency aliases, by default '30min'.

    Returns
    -------
    pd.DataFrame
        _description_
    """
    data = slice_data_by_hour(data, days, timeslot_beg, timeslot_end, "time")

    timeslot_beg = Ctime.from_string(timeslot_beg)
    timeslot_end = Ctime.from_string(timeslot_end)

    # time discretization by freq
    start = datetime.datetime.combine(
        date=data.time.min().date(),
        time=datetime.time(timeslot_beg.hour, timeslot_beg.minute),
        tzinfo=data.time.min().tzinfo,
    )
    end = datetime.datetime.combine(
        date=data.time.max().date(),
        time=datetime.time(timeslot_end.hour, timeslot_end.minute),
        tzinfo=data.time.max().tzinfo,
    )

    if not freq:
        if (timeslot_end - timeslot_beg).hour >= 23 and (
            timeslot_end - timeslot_beg
        ).minute >= 59:
            #
            freq = "1D"
            end += datetime.timedelta(days=1)
        elif (timeslot_end - timeslot_beg).hour > 0:
            freq = f"{(timeslot_end - timeslot_beg).hour}h"
        elif (timeslot_end - timeslot_beg).minute > 0:
            freq = f"{(timeslot_end - timeslot_beg).minute}min"
        else:
            return pd.DataFrame()

    bins_dt = lapin_date_range(start=start, end=end, freq=freq, tz=data["time"].dt.tz)
    bins_str = bins_dt.time.astype(str)

    labels = [f"{bins_str[i][:-3]}" for i in range(1, len(bins_str))]

    data["time"] = pd.cut(
        data["time"], bins=bins_dt, labels=labels, ordered=False, include_lowest=True
    )
    data["time"] = data["time"].astype(str)

    return data


def occupancy_time_aggregation(
    occ_df: pd.DataFrame,
    days: str = "lun-dim",
    timeslot_beg: str = "0h00",
    timeslot_end: str = "23h59",
    freq: str = "30min",
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Compile the occupancy at the granular level of a road segment for
    a given freq. The data must first be matched on the streets using
    the enhancement process.

    Parameters
    ----------
    occ_df : pandas.DataFrame
        Occupancy data for each segment, side_of_street, lap, vehicule
    timeslot_beg : str, optional
        Starting hour for compiling occupancy, by default '0h00'.
    timeslot_end : str, optional
        Stoping hour for compiling occupancy, by default '23h59'.
    freq : str or DateOffset, optional
        Frequency strings can have multiples, e.g. '1h'. See here for a list of
        frequency aliases, by default '30min'.

    Returns
    -------
    occ : pandas.DataFrame
        A db describing each segment's side of street' occupancy by freq.
    veh : pandas.DataFrame
        A db describing each segment's side of street' nb of plate
        read by freq.
    cap : pandas.DataFrame
        A db describing each segment's side of street' capacity by freq.
    restrictions : pandas.DataFrame
        A db describing each segment's side of street' restriction active
        by freq.

    """
    occ_df = occ_df.copy()

    occ_df.rename(columns={"lap_time": "time"}, inplace=True)
    occ_df = associate_time_freq(occ_df, days, timeslot_beg, timeslot_end, freq)

    # parse relevant data
    occ_h = _occup_pivot_handle(
        occ_df,
        pivot_col="occ",
        weight=constants.CAP_N_VEH,
        index=[constants.SEGMENT, constants.SIDE_OF_STREET],
    )
    veh_sighted = _occup_pivot_handle(
        occ_df,
        pivot_col="veh_sighted",
        weight=constants.CAP_N_VEH,
        index=[constants.SEGMENT, constants.SIDE_OF_STREET],
    )
    capacity = _occup_pivot_handle(
        occ_df,
        pivot_col=constants.CAP_N_VEH,
        weight=constants.CAP_N_VEH,
        index=[constants.SEGMENT, constants.SIDE_OF_STREET],
    )
    restrictions = occ_df.pivot_table(
        values=constants.CAP_RESTRICTIONS,
        index=[constants.SEGMENT, constants.SIDE_OF_STREET],
        aggfunc=restriction_aggfunc,
        dropna=False,
        columns="time",
    )
    restrictions = restrictions.rename_axis(None, axis=1)
    restrictions = restrictions.loc[~restrictions.isna().all(axis=1)].reset_index()

    return occ_h, veh_sighted, capacity, restrictions


def agg_regions(
    data: pd.DataFrame,
    regions: pd.DataFrame,
    days: str = "lun-dim",
    timeslot_beg: str = "0h00",
    timeslot_end: str = "23h59",
    freq: str = "30min",
) -> pd.DataFrame:
    """
    Aggregate occupancy by regions. Regions are defined by a set of segments.

    Paramaters
    ----------
    occ: pd.DataFrame
        DataFrame containing occupancy for each segment, sides, vehicule
        and laps.
    regions: pd.DataFrame
        Mapping between street_id and regions to analyse.
    timeslot_beg : str, optional
        Starting hour for compiling occupancy, by default '0h00'.
    timeslot_end : str, optional
        Stoping hour for compiling occupancy, by default '23h59'.
    freq : str or DateOffset, optional
        Frequency strings can have multiples, e.g. '1h'. See here for a list of
        frequency aliases, by default '30min'.

    Returns
    -------
    occ_agg: pd.DataFrame
        Aggregated occupancy for regions.
    """

    data = data.copy()
    data.rename(columns={"lap_time": "time"}, inplace=True)

    data = associate_time_freq(data, days, timeslot_beg, timeslot_end, freq)

    # merge occupancy and regions
    data.drop(columns=constants.SECTEUR_NAME, errors="ignore", inplace=True)

    data = data.join(
        other=regions.set_index([constants.SEGMENT, constants.SIDE_OF_STREET])[
            constants.SECTEUR_NAME
        ],
        on=[constants.SEGMENT, constants.SIDE_OF_STREET],
    )

    data_agg = _occup_pivot_handle(
        occ_df=data,
        pivot_col="occ",
        weight=constants.CAP_N_VEH,
        index=constants.SECTEUR_NAME,
    )

    return data_agg


def get_street_optimum_and_maximum(
    occ_hour: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return the optimum and maximum parking occupancy for every streets.

    Parameters
    ----------
    occ_hour : pd.DataFrame
        Hourly occupancy for every streets. Hours are columns, streets
        are index.

    Returns
    -------
    tuple[pd.DataFrame, pd.DataFrame]
        Optimum and maximum occupancy for every streets.
    """
    occ_hour = occ_hour.copy()
    occ_hour.drop(columns=constants.SEG_DB_GIS, inplace=True, errors="ignore")

    cols = [
        col
        for col in occ_hour.columns
        if col
        not in [
            constants.SEGMENT,
            constants.SIDE_OF_STREET_VIZ,
            constants.SECTEUR_NAME,
            constants.SECTEUR_NAME + "_vis",
            "days",
            "time_interval",
        ]
    ]

    occ_hour_tmp = occ_hour.set_index(
        [constants.SEGMENT, constants.SIDE_OF_STREET_VIZ]
    )[cols]
    occ_hour_tmp = occ_hour_tmp.melt(
        var_name="heure", value_name="occ", ignore_index=False
    )

    def force_float(x):
        try:
            return float(x)
        except ValueError:
            return np.nan

    occ_hour_tmp["occ"] = occ_hour_tmp["occ"].apply(force_float)

    optimum = occ_hour_tmp[(occ_hour_tmp.occ >= 0.8) & (occ_hour_tmp.occ < 0.9)]
    maximum = occ_hour_tmp[(occ_hour_tmp.occ >= 0.9)]

    return optimum, maximum


def street_hourly_formater(
    data: pd.DataFrame, segments: gpd.GeoDataFrame, hour_column: str = None
) -> tuple[pd.DataFrame, pd.Series]:
    """Frame the occupancy dataframe to a human readable format.
    Basically just add the street's name, and between X and Y street.

    Parameters
    ----------
    data : pd.DataFrame
        Street metric dataframe
    segments : pd.DataFrame
        Street name information.
    hour_column : str, optional
        Parse hours in column to make it human readable, by default None.

    Returns
    -------
    tuple[pd.DataFrame, pd.Series]
        Street occupancy formated, Number of streets.
    """
    data = data.copy()
    segments = segments.copy()

    if segments.index.names != [constants.SEGMENT]:
        segments = segments.reset_index()
        segments.drop(columns="index", errors="ignore", inplace=True)
        segments = segments.set_index([constants.SEGMENT])

    data = data.round(2).join(
        other=segments[
            [constants.HR_ROAD_NAME, constants.HR_FROM_ROAD, constants.HR_TO_ROAD]
        ],
        on=[constants.SEGMENT],
    )

    data.reset_index(inplace=True)
    data.drop(columns="index", errors="ignore", inplace=True)

    if hour_column:

        def _parse_hour_format(x):
            try:
                if isinstance(x, int):
                    return f"{x-1}h00 à {x}h00"
                elif isinstance(x, str):
                    return f"{str(int(x[:2])-1).zfill(2)}h00 à {x[:2]}h00"
            except ValueError:
                return x

        data[hour_column] = data[hour_column].apply(_parse_hour_format)

    data = data.set_index(
        [
            constants.SEGMENT,
            constants.SIDE_OF_STREET,
            constants.HR_ROAD_NAME,
            constants.HR_FROM_ROAD,
            constants.HR_TO_ROAD,
        ]
    )

    return data


def _melt_hr_data(
    data: pd.DataFrame,
    metric: str,
    force_float=True,
) -> pd.DataFrame:
    """Melt hourly dataframe if hours are columns.

    Parameters
    ----------
    data : pd.DataFrame
        Hourly metric data.
    metric : str
        Name of the metric

    Returns
    -------
    pd.DataFrame
        Data melted.
    """
    data = data.reset_index()
    data.drop(columns="index", errors="ignore", inplace=True)

    cols = [col for col in data.columns if col != "geometry"]

    data = data.melt(
        id_vars=[constants.SEGMENT, constants.SIDE_OF_STREET],
        value_vars=cols,
        value_name=metric,
        var_name="hour",
    )
    data["hour"] = data["hour"].str.split(":").apply(lambda x: x[0]).astype(int)
    data = data.set_index([constants.SEGMENT, constants.SIDE_OF_STREET, "hour"])

    # force value_col to float
    if force_float:
        mask_numeric = data[metric].apply(is_numeric_transformable)
        data.loc[~mask_numeric, metric] = np.nan
        data[metric] = data[metric].astype(np.float64)

    return data


def merge_occupancy_capacity_vehicule(
    occ_hr: pd.DataFrame,
    cap_hr: pd.DataFrame,
    veh_hr: pd.DataFrame,
    res_hr: pd.DataFrame,
):
    """Merge the three hourly indicator relative to occupancy into one
    DataFrame.

    Parameters
    ----------
    occ_hr : pd.DataFrame
        Occupancy
    cap_hr : pd.DataFrame
        Capacity
    veh_hr : pd.DataFrame
        Vehicule count
    res_hr : pd.DataFrame
        Restrictions active

    Returns
    -------
    pd.DataFrame
        Merged indicators
    """
    occ_hr = _melt_hr_data(occ_hr, "occ")
    cap_hr = _melt_hr_data(cap_hr, "nb_places_total")
    veh_hr = _melt_hr_data(veh_hr, "veh_sighted")
    res_hr = _melt_hr_data(res_hr, "restrictions", force_float=False)

    data = occ_hr.join(veh_hr).join(cap_hr).join(res_hr)

    data["occ"] = data["occ"].astype(float)
    data["nb_places_total"] = data["nb_places_total"].astype(float)
    data["veh_sighted"] = data["veh_sighted"].astype(float)

    return data


def get_optimal_occupancy(
    occ_hr: pd.DataFrame,
    cap_hr: pd.DataFrame,
    veh_hr: pd.DataFrame,
    res_hr: pd.DataFrame,
    seg_gis: gpd.GeoDataFrame,
    optimal_occ_value: float = 0.8,
) -> pd.DataFrame:
    """Create a dataframe with count of optimal segments along with geometry.

    Parameters
    ----------
    occ_hr : pd.DataFrame
        Hourly street's occupancy.
    cap_hr : pd.DataFrame
        Hourly street's capacity.
    veh_hr : pd.DataFrame
        Hourly vehicule count on street.
    res_hr : pd.DataFrame
        Hourly active's restrictions.
    seg_gis : gpd.GeoDataFrame
        Goemetry of the streets.
    otimal_occ_value : float, optional
        Threshold were occupancy starts to be considered optimal, by default
        0.8.

    Returns
    -------
    pd.DataFrame
        Optimal occupancy count of the streets.
    """
    data = merge_occupancy_capacity_vehicule(
        occ_hr=occ_hr, cap_hr=cap_hr, veh_hr=veh_hr, res_hr=res_hr
    )
    data = data.sort_index().dropna(how="all")

    nb_hours_sup_opti = (
        data[(data.occ > optimal_occ_value) & data.restrictions.isna()]
        .groupby(["segment", "side_of_street"])[
            ["veh_sighted", "nb_places_total", "occ", "restrictions"]
        ]
        .agg(["size", "mean"])
    )

    nb_hours_sup_opti = nb_hours_sup_opti.droplevel(0, axis="columns")
    nb_hours_sup_opti.columns = [
        "hour_count",
        "veh_sighted",
        "del",
        "nb_places_total",
        "del",
        "occ",
        "del",
        "restrictions",
    ]
    nb_hours_sup_opti = nb_hours_sup_opti.reset_index()
    nb_hours_sup_opti = nb_hours_sup_opti.drop(columns="del")

    nb_hours_sup_opti = prepare_data_before_export(nb_hours_sup_opti, seg_gis)

    return nb_hours_sup_opti


@deprecated(
    reason="Use lapin.core.study.CollectedAera.occupancy_time_aggregation" + "instead."
)
def occupancy(
    geodbl: gpd.GeoDataFrame,
    enh_lapi: pd.DataFrame,
    res_handler: Curbs,
    timeslot_beg: str = "0h00",
    timeslot_end: str = "23h59",
    freq: str = "30T",
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Compute the aggregated occupancy by a frequence `freq`.

    Parameters
    ----------
    geodbl : gpd.GeoDataFrame
        Geometry of road network (Geobase).
    enh_lapi : pd.DataFrame
        LPR enhanced data.
    res_handler : Curbs
        Curb regulations.
    timeslot_beg : str, optional
        Time window starts, by default '0h00'
    timeslot_end : str, optional
        Time window end, by default '23h59'
    freq : str, optional
        Frequence of analysis, by default '30T'

    Returns
    -------
    tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        Aggregated occupancy, vehicule count and capacity by `freq`
    """
    occ_df = compile_occupancy(enh_lapi)

    if occ_df.empty:
        return pd.DataFrame()

    # extract relevant functions and transform the times:
    #    1 - raw string to datetime
    occ_df["time"] = pd.to_datetime(occ_df.time)
    occ_df["time_sv"] = occ_df["time"].copy()

    #    2 - datetime to ctime
    occ_df["ctime"] = [Ctime.from_datetime(t) for t in occ_df.time]

    #    3 - parse relevant hours
    timeslot_beg = Ctime.from_string(timeslot_beg)
    timeslot_end = Ctime.from_string(timeslot_end)
    occ_df = occ_df[
        (occ_df["ctime"] >= timeslot_beg) & (occ_df["ctime"] <= timeslot_end)
    ]
    occ_df.drop(columns="ctime", inplace=True)

    #    4 - time discretization by freq
    start = datetime.datetime.combine(
        date=occ_df.time.min().date(),
        time=datetime.time(timeslot_beg.hour, timeslot_beg.minute),
        tzinfo=occ_df.time.min().tzinfo,
    )
    end = datetime.datetime.combine(
        date=occ_df.time.max().date(),
        time=datetime.time(timeslot_end.hour, timeslot_end.minute),
        tzinfo=occ_df.time.max().tzinfo,
    )

    if not freq:
        if (timeslot_end - timeslot_beg).hour >= 23 and (
            timeslot_end - timeslot_beg
        ).minute >= 59:
            #
            freq = "1D"
            end += datetime.timedelta(days=1)
        elif (timeslot_end - timeslot_beg).hour > 0:
            freq = f"{(timeslot_end - timeslot_beg).hour}H"
        elif (timeslot_end - timeslot_beg).minute > 0:
            freq = f"{(timeslot_end - timeslot_beg).minute}T"
        else:
            return pd.DataFrame()

    time_period = "hour"
    if (timeslot_end - timeslot_beg).hour > 1:
        time_period = "all"

    bins_dt = lapin_date_range(start=start, end=end, freq=freq, tz=occ_df["time"].dt.tz)
    bins_str = bins_dt.time.astype(str)

    labels = [f"{bins_str[i][:-3]}" for i in range(1, len(bins_str))]

    occ_df["time"] = pd.cut(occ_df["time"], bins=bins_dt, labels=labels, ordered=False)
    occ_df["time"] = occ_df["time"].astype(str)

    # parse relevant data
    occ_h = _occup_h_pivot_handle(
        occ_df,
        geodbl,
        res_handler,
        pivot_col="occ",
        weight=constants.CAP_N_VEH,
        time_period=time_period,
    )
    veh_sighted = _occup_h_pivot_handle(
        occ_df, geodbl, res_handler, pivot_col="veh_sighted", time_period=time_period
    )
    capacity = _occup_h_pivot_handle(
        occ_df,
        geodbl,
        res_handler,
        pivot_col=constants.CAP_N_VEH,
        time_period=time_period,
    )

    # force int type in the capacity strings
    def try_to_force_int_string(x):
        if not isinstance(x, str):
            return x
        try:
            return str(int(float(x)))
        except ValueError:
            return x

    capacity = capacity.applymap(try_to_force_int_string)

    return occ_h, veh_sighted, capacity


@deprecated(
    reason="Use lapin.core.study.CollectedAera.occupancy_time_aggregation" + "instead."
)
def _occup_h_pivot_handle(
    occ_df, geodbl, resh, pivot_col="occ", weight=None, time_period="hour"
):
    """Aggregate the occupation at the segment and side of street level. The
    aggregation is parametred by attribute pivot_col. Default is aggregated i
    value is occupancy. In addition, restrictions are applied even if no
    data is recolted by the LAPI vehicule.

    Paramaters
    ----------
    occ_df : pandas.DataFrame
        Unagregated occupancy computed for each segment on each lap of a LAPI
        vehicule.
    geodbl : geopandas.GeoDataFrame
        Geographical data of roads side of street.
    restrictionHandler : analysis.restrictions.RestrictionHandler
        An instance of the restriction engine for this LAPI data.
    pivot_col : string (Default: 'occ')
        Column values that will be aggregated.

    Returns
    -------
    aggregated_data : geopandas.GeoDataFrame
       Data aggregated at side of street level with restrictions when it
       applies.
    """

    # pivot this to have a column per hour
    occ_h = occ_df.pivot_table(
        pivot_col,
        index=[constants.SEGMENT, constants.SIDE_OF_STREET_VIZ],
        aggfunc=lambda x: restriction_aggfunc(
            x.to_list(),
            weight=occ_df.loc[x.index, weight].to_list() if weight else weight,
        ),
        columns="time",
        dropna=False,
    )
    occ_h = occ_h.loc[~occ_h.isna().all(axis=1)].reset_index()

    # add all the roads in the analysis zone
    complete = expand_network(occ_h, geodbl)

    # enforce restrictions
    return enforce_restrictions(
        complete, resh, zero_observ=False, time_period=time_period
    )


@deprecated(reason="Use lapin.core.study.CollectedArea.to_dataframe instead")
def compile_occupancy(enh_lapi):
    """
    Compile the occupancy on each side of street segments. The data must first
    be matched on the streets using the enhancement process.

    Parameters
    ----------
    enhLapi : pandas.DataFrame
        The sighting data, must have been ran through the enhancement process
        beforehand.
        Data must containing the number of spaces in the network (either
        in meters with a column named 'Espace_stationnement (m)' or in car
        spaces with a column named 'nb_places') and restrictions to those
        places compiled with columns named 'restrictions', 'res_hour_from',
        'res_hour_to', and 'res_days'.
    occup_on : str, optional
        The method to use to calculate the occupancy. The choices are 'meter'
        to calculate directly from the footprint of the sighted vehicules vs
        the availaible space or 'veh' to transform the available space in
        car-equivalent spaces and compare on a car vs acr-equiv. basis.
        Default 'meter'.

    Raises
    ------
    ValueError
        Indicate that segment_geodbl_geom is not present, which means that the
        enhancement process was not ran prior to calling this function.

    Returns
    -------
    occ_df : geopandas.GeoDataFrame
        A db describing each segment's side of street' occupancy.

    """
    if enh_lapi.empty:
        return pd.DataFrame()

    if "lap_id" not in enh_lapi.columns:
        raise IncompleteDataError(
            "lapi_id", "enhLapi", "Try running the enhancement process first."
        )

    # 1- Aggregate at <segment, side_of_street, lap_id> level
    grouped = enh_lapi.groupby(
        [constants.SEGMENT, constants.SIDE_OF_STREET_VIZ, "lap_id"]
    )
    res = grouped.agg(
        {constants.PLATE: "count", "lap_time": "first", constants.CAP_N_VEH: "first"}
    ).rename(columns={constants.PLATE: "veh_sighted", "lap_time": "time"})

    res["time"] = pd.to_datetime(
        res["time"], **enh_lapi.parameters.get("date_kwargs", {})
    )

    # we'll need to change the index real soon
    res = res.reset_index()

    res["occ"] = res["veh_sighted"] / res[constants.CAP_N_VEH].astype(float)

    # We have stopped mixing str and int in the same columns.
    # Aucune place is a synonyme of 0. The occ should not be taken
    # into account cause we do a weigthed mean on CAP_N_VEH.
    res["occ"] = res.apply(
        lambda x: x["occ"] if x[constants.CAP_N_VEH] != 0 else 0, axis=1
    )

    return res
