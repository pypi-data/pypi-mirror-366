# -*- coding: utf-8 -*-
"""
Created on Wed Jun  9 10:12:27 2021

@author: lgauthier
@author: alaurent
"""

from copy import deepcopy
from typing import List, Tuple
from datetime import datetime

import numpy as np
import pandas as pd

from lapin import constants
from lapin.tools.utils import restriction_aggfunc
from lapin.models.utils import slice_data_by_hour


def get_breaks(
    lap_list: List[int], distance_list: List[float], dist_m: float = 5.5
) -> List[List[int]]:
    """For a given list of sequentials lap_id and a distance_list representing
    the position of the immobilisation on the street, find the consecutives lap
    in the lap_list.

    Parameters
    ----------
    lap_list : list of int
        A list of lap identifier for a given immobilisation. Usually during the
        all observation periods.
    distance_list : list of float
        Distances of the immobilisation on the road segment. The length should
        be the same as lap_list.
    dist_m : float
        Tolerance accepted on distances between one immo and an other. If two
        lap are consecutive but distances are greater than one place between
        immo, we considere it to be two different immo (i.e. there is a break).

    Return
    ------
    list[list[int]] (e.g. [[1,12], ...])
           List of interval of immobilisations. Each interval represent the
           first lap identifier and the last one of an immobilisation.
    """
    retlist = []
    # Avoid IndexError for  random_list[i+1]
    indx_s = 0
    indx_f = 0
    for i in range(len(lap_list) - 1):
        # Check if the next number is consecutive
        if (lap_list[i] + 1 == lap_list[i + 1]) and (
            (distance_list[i + 1] - dist_m)
            <= distance_list[i]
            <= (distance_list[i + 1] + dist_m)
        ):
            indx_f += 1
        else:
            # If it is not append the count and restart counting
            retlist.append([lap_list[indx_s], lap_list[indx_f]])
            indx_s = i + 1
            indx_f = i + 1
    # Since we stopped the loop one early append the last count
    retlist.append([lap_list[indx_s], lap_list[indx_f]])

    return retlist


def get_time_lap_interval(
    laps_info: pd.DataFrame, lap_interval: List[int]
) -> Tuple[int, datetime, datetime, bool]:
    """Retrieve the duration of an immosilisation based on it's starting and
    ending lap. Parking time is the results of the mean between maximum  and
    minimum time a vehicule could have stay (resp. 'at_more' and 'at_least').

    In details, parking time is computed as follow:

        1. If the starting (resp. ending) lap is the first (resp. last) lap of
        the day, we cannot determine how many time the vehicule has stayed put.
        Thus we use the difference of the ending time of the last lap with the
        beggining time of the first lap to infer stay duration. We classify
        this result by is_first_last columns, meaning the car can have stayed
        longer.

        2. Otherwise, we now for sure that the vehicule has entered and left
        it's parking spot within the observation day. The parking time is then
        infered as the mean between minum stay and maximum stay. In the first
        hand, maximum stay is defined as the beggining time of the next lap
        after the last seen lap minus the last time of the previous lap before
        the first seen lap. In the other hand, minimum parking time is defined
        as the difference between the last time seen lap and the first time
        seend lap time.

    Paramaters
    ----------
    laps_info : pandas.DataFrame
        DataFrame of first and last time of each lap. Index must be lap
        indentifier and there should be at least two columns : first and last.

    lap_interval : list of two ints. (e.g. [1, 2]).
        An continuous lap interval. First is the identifier of the starting
        lap, second is the identifier of the ending lap.

    Returns
    -------
    time_duration : int.
        Seconds of immobilisation.
    time_of_park : datetime.
        Infered arrival time of the vegicule in the parking lot.
    time_of_leave : datetime.
        Infered departure time of the vegicule.
    first_or_last : boolean.
        If true then the vehicule was present on the first or last run of the
    enforcement car.
    """

    # one of the born is the first or last lap
    first_or_last = False
    if lap_interval[0] == laps_info.index[0] or lap_interval[1] == laps_info.index[-1]:
        first_or_last = True

    # get the lap_start and the lap_stop
    lap_start = laps_info.loc[lap_interval[0], "first"]
    lap_stop = laps_info.loc[lap_interval[1], "last"]

    # at least parking time
    td = lap_stop - lap_start
    at_least = td.total_seconds()

    # at most parking time
    start_shift = 1
    end_shift = 1
    if first_or_last:
        if lap_interval[0] == laps_info.index[0]:
            start_shift = 0
        if lap_interval[1] == laps_info.index[-1]:
            end_shift = 0

    prev_lap_stop = laps_info.loc[lap_interval[0] - start_shift]["last"]
    next_lap_start = laps_info.loc[lap_interval[1] + end_shift]["first"]
    td = max(next_lap_start, lap_stop) - min(prev_lap_stop, lap_start)

    at_most = td.total_seconds()

    # parking time estimation
    park_time = np.mean([at_least, at_most])

    # estimed arrival_time
    arrival_time = (
        min(prev_lap_stop, lap_start) + (lap_start - min(prev_lap_stop, lap_start)) / 2
    )

    # estimed departure time
    departure_time = lap_stop + (max(next_lap_start, lap_stop) - lap_stop) / 2

    return park_time, arrival_time, departure_time, first_or_last


def get_lap_time_info(enh_lapi: pd.DataFrame) -> pd.DataFrame:
    """Compute laps time start and end for all segments.

    Paramaters
    ----------
    enhLapi : pandas.DataFrame
        The enhance version of the lapi readings.

    Returns
    -------
    seg_lap_info : pandas.DataFrame
        For each segment and lap, the first and last time of passage.
    """
    data = enh_lapi.copy()
    data.sort_values(
        [constants.SEGMENT, constants.SIDE_OF_STREET, "day", "lap", "datetime"],
        inplace=True,
    )
    return data.groupby([constants.SEGMENT, constants.SIDE_OF_STREET, "day", "lap"])[
        "datetime"
    ].agg(["first", "last"])


def compile_parking_time(
    enh_lapi: pd.DataFrame,
    seg_lap_info: pd.DataFrame = None,
    days: str = "lun-dim",
    timeslot_beg: str = "0h00",
    timeslot_end: str = "23h59",
) -> pd.DataFrame:
    """Compile the parking occupancy for each segment and side of street.
    Parking time is based on the number of sequential lap a vehicule as been
    sighted. When a vehicule is present on the last lap or on the first lap,
    the value of columns 'is_first_last' is True. Time span is express in
    seconds.

    Parameters
    ----------
    enhLapi : pandas.DataFrame
        The enhance version of the lapi readings.

    Returns
    -------
    parking_time : pandas.DataFrame
        Parking time for each consecutive stay on a side of a segment for each
        vehicule express in seconds. Each stayed duration comes with a mention
        'at_least' or 'at_more'. First and last lap identifier of a stay is
        also added to the data.
    """
    data = enh_lapi.copy()
    data.datetime = pd.to_datetime(data.datetime)
    data["day"] = data.datetime.dt.date

    data = slice_data_by_hour(data, days, timeslot_beg, timeslot_end, "datetime")

    # compute start and ending time of each lap for each segment
    if not (isinstance(seg_lap_info, pd.DataFrame) or seg_lap_info):
        seg_lap_info = get_lap_time_info(data)

    # compute parking time
    grouped = data.groupby([constants.SEGMENT, constants.SIDE_OF_STREET, "day"])
    datas = []
    for cur_seg, group in grouped:
        # sort grouped data by lap and not datetime
        group.sort_values("lap", inplace=True)

        # retrive lap time information for this segment
        laps_info = seg_lap_info.loc[cur_seg].copy()

        # make lap consecutive if they aren't
        laps_info.reset_index(inplace=True)

        # second time to get a column 'index'
        laps_info.reset_index(inplace=True)
        laps_info.rename(columns={"lap": "conseq_lap"}, inplace=True)

        laps_info.set_index("conseq_lap", inplace=True)

        # find sequential lap for each plaque
        plaqued = group.groupby(constants.PLATE)

        plaque_consecutive_lap_index = (
            plaqued[["lap", constants.POINT_ON_STREET]]
            .apply(
                lambda x: get_breaks(
                    x.lap.to_list(), x[constants.POINT_ON_STREET].to_list(), dist_m=5.50
                )
            )
            .to_frame("intervals")
        )

        # compute stayed time for each vehicule
        plaques = []
        for plaque, intervals in plaque_consecutive_lap_index.iterrows():
            for interval in intervals.values[0]:
                p = group[
                    np.logical_and(
                        group[constants.PLATE] == plaque, group.lap == interval[0]
                    )
                ].copy()
                p["lap_start"] = p["lap"]
                p["lap_end"] = interval[1]
                p["nb_lap"] = 1 + interval[1] - interval[0]

                # park_time
                (parktime, ar_time, dep_time, first_or_last) = get_time_lap_interval(
                    laps_info, interval
                )
                p["park_time"] = parktime
                p["arrival_time"] = ar_time
                p["departure_time"] = dep_time
                p["first_or_last"] = first_or_last

                plaques.append(p)

        plaques = pd.concat(plaques)
        datas.append(plaques)

    # Aggregate data
    park_time = pd.concat(datas)

    return park_time


def park_time_street(park_time, res_handler, seg_gis, handle_restriction):
    """Compute the average parking time of each segment present in seg_gis.

    This function average the parking time of each immobilisation on a segment
    and not the parking time of each observation on the segments. Meaning that
    a car that have stayed 3 hours will count as one (and not as the number
    of observation made of this car) in the averaging function.

    Parameters
    ----------
    park_time : pandas.DataFrame
        The parking time compilation for each immobilisation. Must contain
        'park_time', 'segment' and 'side_of_streets' columns.
    seg_info : pandas.DataFrame
        Information about the segment and side of street parking capaicty
        and regulations. Must containts 'segment', 'side_of_street' columns.
    seg_gis : geopandas.GeoDataFrame
        Geometry of each <segment, side_of_street> object. Must have columns
        'ID_TRC' and 'COTE'.
    handle_restriction : bool (default is True).
        If True, parse restrictions from parking time dataset.

    Returns
    -------
    park_time_street : geopandas.GeoDataFrame
       Parking time averaged at <segment, side_of_street> level

    TODO
    ----
    Raise imcompleteDataError for missing columns in DataFrame
    """
    park_time = park_time.copy()

    # 1 - Aggregate parking time by segment
    pt_street = (
        park_time.groupby([constants.SEGMENT, constants.SIDE_OF_STREET])["park_time"]
        .agg(lambda x: restriction_aggfunc(x, stats_type="median"))
        .reset_index()
    )

    return pt_street


def park_time_distribution(
    park_time: pd.DataFrame, level: str = "secteur"
) -> pd.DataFrame:
    """Compute the parking time distribution for all immobilisation at
    <level> granular level.

    This function the parking time distribution of each immobilisation on a
    segment and not the parking time of each observation on the segments.
    Meaning that a car that have stayed 3 hours will count as one (and not
    as the number of observation made of this car) in the averaging function.

    Parameters
    ----------
    park_time : pandas.DataFrame
        The parking time compilation for each immobilisation. Must contain
        'park_time', 'segment' and 'side_of_streets' columns.
    seg_info : pandas.DataFrame
        Information about the segment and side of street parking capaicty
        and regulations. Must containts 'segment', 'side_of_street' columns.
    level : str. Default 'secteur'.
       The granular level of interest. Supported level are 'segment' and
       'secteur'.
    handle_restriction : bool (default is True).
        If True, parse restrictions from parking time dataset.

    Returns
    -------
    park_time_dist : pandas.DataFrame
       Parking time distribtion at <level> level granular level.

    Raise:
    ------
    NotImplementedError:
        If passing a <level> granular level that is not implemented.

    TODO
    ----
    1. Raise imcompleteDataError for missing columns in DataFrame
    2. Store the numeric cuts somewhere to not have it defined in each function
    that use them.
    """
    park_time = park_time.copy()

    # 1 - Convert park time to hour
    park_time["h_pt"] = park_time.park_time / 3600

    # 2 - Categorize the parking time
    numeric_cuts = {
        "Très court": 0.5,
        "Court": 2,
        "Moyen": 5.5,
        "Long": max(24, park_time.h_pt.max()),
    }
    labels = list(numeric_cuts.keys())
    # cut
    park_time["category"] = pd.cut(
        park_time.h_pt,
        [0] + list(numeric_cuts.values()),
        labels=labels,
        include_lowest=True,
    ).astype(str)
    park_time.loc[park_time.first_or_last, "category"] = "Temps indéterminé"
    labels += ["Temps indéterminé"]

    # 3 - retrieve restriction on roads segments
    # get string data
    pt_cat = park_time[
        [
            not (pd.api.types.is_numeric_dtype(type(x)) or pd.isna(x))
            for x in park_time.park_time
        ]
    ].copy()
    park_time.loc[pt_cat.index, "category"] = pt_cat.park_time

    # 4 - count parktime by time category and spatial level
    if level == "secteur":
        # aggregate and fil
        # change aggfunc to sum if you want the observation distribter
        park_time_distrib = park_time.pivot_table(
            "nb_lap", index="category", aggfunc="count"
        ).filter(items=labels, axis=0)
        # normalize
        park_time_distrib = park_time_distrib.div(park_time_distrib.sum()).multiply(100)
        names = "category"
    elif level == constants.SEGMENT:
        # aggregate
        # change aggfunc to sum if you want the observation distribter
        park_time_distrib = park_time.pivot_table(
            "nb_lap",
            index=[constants.SEGMENT, constants.SIDE_OF_STREET, "category"],
            aggfunc="count",
        ).reset_index()
        # filter
        park_time_distrib = park_time_distrib.loc[
            park_time_distrib.category.isin(labels)
        ]
        # normalize
        park_time_distrib.set_index(
            ["segement", constants.SIDE_OF_STREET, "category"], inplace=True
        )
        park_time_distrib = park_time_distrib.div(park_time_distrib.sum()).multiply(100)
        names = [constants.SEGMENT, constants.SIDE_OF_STREET, "category"]
    else:
        raise NotImplementedError(f"There is no aggregation function for {level}")

    return park_time_distrib.reset_index(names=names)


def categorize_parking_usage(park_time, occ_ts, numeric_cuts=None):
    """Compute the usage of parking slot by category of parking time
    for all the secteur.

    This function compute the distribution of the parking time category of
    each observation on a segment and not the parking time category of each
    immobilisation on the segments. Meaning that a car that have stayed 3
    hours will count as the number of observation made of that car (and not as
    one) in the averaging function.

    Parameters
    ----------
    park_time : pandas.DataFrame
        The parking time compilation for each immobilisation. Must contain
        'park_time', 'segment' and 'side_of_streets' columns.
    occ_ts : pandas.DataFrame
        Average occupancy of each <segment, side_of_street> for the total
        observation period.
    seg_info : pandas.DataFrame
        Information about the segment and side of street parking capaicty
        and regulations. Must containts 'segment', 'side_of_street' columns.
    handle_restriction : boo (default is True).
        If True, parse restrictions from parking time dataset.

    Returns
    -------
    usage_categorisation : pandas.DataFrame
       Categorisation of the total ccupancy.

    TODO
    ----
    1. Raise imcompleteDataError for missing columns in DataFrame
    2. Store the numeric cuts somewhere to not have it defined in each function
    that use them.
    """
    park_time = park_time.copy()
    occ_ts = occ_ts.copy()

    # 1 - Convert park time to hour
    park_time["h_pt"] = park_time.park_time / 3600

    # 2 - Categorize the parking time
    if not numeric_cuts:
        numeric_cuts = {
            "Très court": 0.5,
            "Court": 2,
            "Moyen": 5.5,
            "Long": max(24, park_time.h_pt.max()),
        }
    else:
        numeric_cuts = deepcopy(numeric_cuts)
    labels = list(numeric_cuts.keys())

    # Parking that we can assert the time parked
    park_time["category"] = pd.cut(
        park_time.h_pt,
        [0] + list(numeric_cuts.values()),
        labels=labels,
        include_lowest=True,
    ).astype(str)

    # Parking where we **cannot** assert the time parked
    numeric_cuts_ind = {
        "Indéterminé " + label: value for label, value in numeric_cuts.items()
    }
    labels_ind = list(numeric_cuts_ind.keys())
    park_time.loc[park_time.first_or_last, "category"] = pd.cut(
        park_time[park_time.first_or_last].h_pt,
        [0] + list(numeric_cuts_ind.values()),
        labels=labels_ind,
        include_lowest=True,
    ).astype(str)

    labels += labels_ind
    numeric_cuts.update(numeric_cuts_ind)

    # 5 - Compute parking occupation usage by <segment, side_of_street>
    #     and category

    # Here each observation count as one (vs each immo count as one) to take
    # into account that a long parking time will appear as one row in the table
    # but occup several lap. Meanwhile a short parking time will appear at each
    # lap. In short we want to compute average occupancy of parking category,
    # so at each lap we count how many cars are in each category of time.
    cat_park_time = park_time.pivot_table(
        "nb_lap",
        index=[constants.SEGMENT, constants.SIDE_OF_STREET],
        columns="category",
        aggfunc="sum",
    )
    cat_park_time = cat_park_time.div(cat_park_time.sum(axis=1), axis=0).fillna(0)

    # this is to uncategorized the columns type
    cat_park_time.columns = cat_park_time.columns.to_list()

    # join parking time with occupancy information and segment information
    if occ_ts.index.names != [constants.SEGMENT, constants.SIDE_OF_STREET]:
        occ_ts.set_index([constants.SEGMENT, constants.SIDE_OF_STREET])

    cat_park_time = cat_park_time.join(occ_ts)

    # 6 - Compute occupancy proportion of each type of parking
    cols_cat = np.intersect1d(labels, cat_park_time.columns)
    cols_cat = sorted(cols_cat, key=lambda x: numeric_cuts[x])

    for col in cols_cat:
        cat_park_time[col] = [
            cat * occ if not isinstance(occ, str) else 0
            for (cat, occ) in zip(cat_park_time[col], cat_park_time["mean_occ"])
        ]

    # get inocupied parking slot proportion
    cat_park_time = cat_park_time.reindex(columns=cols_cat + ["weight"])
    cat_park_time[constants.REMPL_CAT_NO_PARK] = [
        1 - occ_sum if occ_sum > 0 else 0
        for occ_sum in cat_park_time[cols_cat].sum(axis=1).fillna(0)
    ]

    # 7 - Remove street with no parking space
    cat_park_time = cat_park_time[
        cat_park_time[list(cols_cat) + [constants.REMPL_CAT_NO_PARK]].sum(axis=1) != 0
    ]

    return cat_park_time.reset_index()


def parking_time_by_provenance(park_time, trips, classe_dist=[0, 1, 3, 7, 15, np.inf]):
    """Compute the distribtion of parking time by provenance.

    This function compute the parking time distribution of each immobilisation
    on a segment and not the parking time of each observation on the segments.
    Meaning that a car that have stayed 3 hours will count as one (and not
    as the number of observation made of this car) in the averaging function.

    Parameters
    ----------
    park_time : pandas.DataFrame
        The parking time compilation for each immobilisation. Must contain
        'park_time', 'segment' and 'side_of_streets' columns.
    trips : pandas.DataFrame
        Trips made by a car to park at parking slot.
    seg_info : pandas.DataFrame
        Information about the segment and side of street parking capaicty
        and regulations. Must containts 'segment', 'side_of_street' columns.
    classe_dist : list. Default [0, 1, 3, 7, 15, np.inf]
        Classes of distances in KM.
    handle_restriction : bool (default is True).
        If True, parse restrictions from parking time dataset.

    Returns
    -------
    park_time_prov : pandas.DataFrame
       Distribution of parking time by provenance.

    TODO
    ----
    1. Raise imcompleteDataError for missing columns in DataFrame
    2. Store the numeric cuts somewhere to not have it defined in each function
    that use them.
    3. Put in a function all the code that is copied/pasted in the 3 functions
    aboved.
    """

    park_time = park_time.copy()
    trips = trips.copy()

    # 1 - convert park time to hour
    park_time["h_pt"] = park_time.park_time / 3600

    # 2 - categorize the parking time
    numeric_cuts = {
        "Très court": 0.5,
        "Court": 2,
        "Moyen": 5.5,
        "Long": max(24, park_time.h_pt.max()),
    }
    labels = list(numeric_cuts.keys())
    # cut
    park_time["category"] = pd.cut(
        park_time.h_pt,
        [0] + list(numeric_cuts.values()),
        labels=labels,
        include_lowest=True,
    ).astype(str)

    # 3 - categorize distance time
    classe_str = [f"<{i} km" for i in classe_dist[1:-1]] + [f"{classe_dist[-2]}+ km"]
    trips["dist_class"] = pd.cut(
        trips.dist_ori_m / 1000, bins=classe_dist, labels=classe_str
    )
    trips.columns = trips.columns.to_list()

    # 4 - retrieve restriction on roads segments
    # filter string
    pt_cat = park_time[
        [
            not (pd.api.types.is_numeric_dtype(type(x)) or pd.isna(x))
            for x in park_time.park_time
        ]
    ].copy()
    park_time = park_time.loc[~park_time.index.isin(pt_cat.index)]

    # 5 - Join trips with parking time
    park_time = park_time.merge(
        trips,
        left_on=[
            constants.SEGMENT,
            constants.SIDE_OF_STREET,
            constants.PLATE,
            "lap_start",
        ],
        right_on=[
            constants.SEGMENT,
            constants.SIDE_OF_STREET,
            constants.PLATE,
            constants.LAP,
        ],
        how="left",
    )

    # 6 - Compute dist_class by category distribution
    park_time = (
        park_time.groupby(["dist_class", "category"])
        .size()
        .to_frame("Pourcentage d'immobilisation totale")
    )
    # normalize
    park_time /= park_time.sum()
    park_time *= 100
    park_time.reset_index(inplace=True)

    return park_time
