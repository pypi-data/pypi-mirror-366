"""Everything related to laps """

import pandas as pd
import numpy as np

from lapin import constants
from lapin.core import TrajDataFrame, LprDataFrame
from lapin.tools.utils import IncompleteDataError


def _lap_sequence_by_time(
    data: TrajDataFrame, delta_treshold: int = 10
) -> TrajDataFrame:
    """Create primary_lap columns in the TrajDataFrame. The computation method
    is by time. When a vehicule enter a segment the lap begin, if the gap
    between two value is greater than the thresold, a new lap is created.

    Parameters
    ----------
    data : TrajDataFrame
        Positions of the vehicules.
    delta_treshold : int, optional
        Threshold in second that indicate a lap as passed
        between two readings, by default 10.

    Returns
    -------
    TrajDataFrame
        Initial dataframe with added column 'primary_lap' and
        'primary_lap_time'
    """
    data.sort_values(constants.DATETIME, inplace=True)

    grouped = data.groupby([constants.SEGMENT, "dir_veh", constants.UUID])
    groups = []
    for _, group in grouped:
        group["td"] = [0] + [
            td.total_seconds()
            for td in np.asarray(group.datetime.tolist())[1:]
            - np.asarray(group.datetime.tolist())[:-1]
        ]
        group["primary_lap"] = (group.td > delta_treshold).cumsum()
        # each vehicule should have a different start lap
        group["primary_lap"] = group["primary_lap"]
        # get first lap time of every lap
        group["primary_lap_time"] = group.groupby("primary_lap")[
            constants.DATETIME
        ].transform("first")
        # save data
        groups.append(group.drop(columns=["td"]))

    data = pd.concat(groups)

    return data


def _lap_sequence_by_seg(tdf: TrajDataFrame) -> TrajDataFrame:
    """Create primary_lap columns in the TrajDataFrame. The computation method
    is by segment. When a vehicule enter a segment the lap begin, when it
    leaves it, the lap ends.

    Parameters
    ----------
    tdf : TrajDataFrame
        Positions of the vehicules

    Returns
    -------
    TrajDataFrame
        Initial dataframe with added column 'primary_lap' and
        'primary_lap_time'
    """

    tdf = tdf.sort_values([constants.UUID, constants.DATETIME])

    # sequence each lap on a changing segment
    tdf["seq"] = tdf.groupby(constants.UUID)[constants.SEGMENT].transform(
        lambda x: (x.diff() != 0).cumsum()
    )

    # label lap from 1 to n for each car and segment
    tdf["primary_lap"] = tdf.groupby([constants.UUID, constants.SEGMENT])[
        "seq"
    ].transform(lambda x: (x.diff() != 0).cumsum())

    tdf["primary_lap_time"] = tdf.groupby(
        [constants.UUID, constants.SEGMENT, "primary_lap"]
    )[constants.DATETIME].transform("first")

    tdf = tdf.drop(columns="seq")

    return tdf


def compute_veh_lap_on_segment(
    data: TrajDataFrame, method: str = "time", time_treshold: int = 10
):
    """Create primary_lap and primary_lap_time columns in the DataFrame.
    Lap is infered for each road segment and vehicules that passed on it. If
    reading for a road segment by a vehicule have a gap of more than
    delta_treshold second, then a lap is created. The primary_lap_time is
    infered as the first reading that makes the lap.

    Parameters
    ----------
    data: TrajDataFrame
        Trajectory dataframe
    delta_treshold: int (Default:10)
        Time threshold used to infer laps, in seconds.
    method: str, optional in 'time' or 'sequence'
        Method used to compute lap. Default value is 'time'

    Returns
    -------
    data: pd.DataFrame
        Class data enhance with a primary lap sequence.

    Raises
    ------
    IncompleteDataError
        data must have segment column.
    ValueError
        Method can only be one of the following : 'time', 'segment'.
    """

    data = data.copy()

    if constants.SEGMENT not in data.columns:
        raise IncompleteDataError(
            data, constants.SEGMENT, "Data must have segment column."
        )

    # standardize uuid to sequencial integer
    data = data.assign(
        veh_id=data[constants.UUID].map(
            {
                data[constants.UUID].unique()[i]: i + 1
                for i in range(len(data[constants.UUID].unique()))
            }
        )
    )

    if method == "time":
        return _lap_sequence_by_time(data, time_treshold)
    if method == "segment":
        return _lap_sequence_by_seg(data)

    raise ValueError(
        f"Method {method} is not implemented. Please choose between"
        + "'time' and 'segment'."
    )


def _create_lap_offset(data: TrajDataFrame, sort: bool = True) -> list:
    """Detect indexes where the uuid of the vehicule changes. Return an
    increment for each vehicule to make sure their lap index + increment is
    unique.

    Parameters
    ----------
    data: TrajDataframe
        TrajDataframe to compute the offset on

    Returns
    -------
    list
        list of shape of data, containing the offset to make lap_id unique on
        the whole dataset.
    """

    data = data.copy()
    if sort:
        data = data.sort_by_uid_and_datetime()
    offset = np.zeros(data.shape[0])
    idx_change = (
        np.where(data.groupby(constants.UUID).transform("size").diff(-1) != 0)[0][:-1]
        + 1
    )
    offset[idx_change] = data.groupby(constants.UUID).size().values[:-1]

    return offset.cumsum()


def compute_lpr_lap_sequences(
    data: TrajDataFrame, method: str = "time", time_treshold: int = 10
) -> LprDataFrame:
    """Adds lap and lap_time columns. Compute consecutive lap sequence
    for all the segment and all the readings, independently of the vehicule
    that collected it. Based on Enhancer.primary_lap_sequence.

    If two vehicules starts a lap on the same segment as the same time,
    prevalance if accorded to one vehicule arbitrary. This prevalance is
    conserved for all others occurences of this scenario.

    Parameters
    ----------
    data: TrajDataFrame
        Plates position data.
    method: str, optional
        Lap computation method. Either 'time' or 'segment'
    delta_treshold: int, optional
        Time threshold used to infer laps, in seconds.

    Returns
    -------
    data: pd.DataFrame
        Class data enhance with a primary lap sequence.
    """

    data = compute_veh_lap_on_segment(data, method, time_treshold)

    # create a unique lap_time independant of the vehicule uuid
    data["primary_lap"] += _create_lap_offset(data)
    # sort data by primary_lap_time
    data.sort_values(["primary_lap_time", constants.DATETIME], inplace=True)

    group_column = [constants.SEGMENT]
    if method == "time":
        group_column += ["dir_veh"]

    data["lap"] = data.groupby(group_column)["primary_lap"].transform(
        lambda x: (x.diff() != 0).cumsum()
    )

    data["lap_id"] = (
        "veh" + data["veh_id"].astype("str") + "_" + data["lap"].astype("str")
    )

    # data cleaning
    data.rename(columns={"primary_lap_time": "lap_time"}, inplace=True)
    data.drop(columns="primary_lap", inplace=True, errors="ignore")
    data.drop(columns="veh_id", inplace=True, errors="ignore")

    return data


def lap_smoothing(data: LprDataFrame, max_lap_creation: int = 3600):
    """Heuristic to add fake observations in Enhancer data. A fake
    observation is added when a vehicule observed is part of same
    geographical cluster and there is a lap gap beetween one observation
    and the next.

    Returns
    -------
    data: pd.DataFrame

    Example
    -------

    Consider the following data:
    >>> data.head()
    |     segment | plaque   |   cluster_id | uuid |   lap | lap_id
    |------------:|:---------|-------------:|:-----|------:|:---------
    | 1.39006e+06 | G250     |            0 | 0    |    10 | veh2_10
    | 1.39006e+06 | G250     |            0 | 0    |    14 | veh2_14
    | 1.39006e+06 | G250     |            0 | 1    |    17 | veh1_17

    | lap_time            | datetime            |
    |:--------------------|:--------------------|
    | 2022-06-21 16:08:16 | 2022-06-21 16:08:25 |
    | 2022-06-21 19:06:25 | 2022-06-21 19:06:29 |
    | 2022-06-21 20:08:16 | 2022-06-21 20:08:22 |

    We can see that lap 11, 12, 13, 15 and 16 are missing but that the
    vehicule is part of the same cluster.

    >>> lap_smoothing(data)
    >>> data.head()
    |     segment | plaque   |   cluster_id | uuid |   lap | lap_id
    |------------:|:---------|-------------:|:-----|------:|:---------
    | 1.39006e+06 | G250     |            0 | 0    |    10 | veh2_10
    | 1.39006e+06 | G250     |            0 | 0    |    11 | veh1_11
    | 1.39006e+06 | G250     |            0 | 0    |    12 | veh1_12
    | 1.39006e+06 | G250     |            0 | 0    |    13 | veh2_13
    | 1.39006e+06 | G250     |            0 | 0    |    14 | veh2_14
    | 1.39006e+06 | G250     |            0 | 0    |    15 | veh1_15
    | 1.39006e+06 | G250     |            0 | 0    |    16 | veh2_16
    | 1.39006e+06 | G250     |            0 | 1    |    17 | veh1_17

    | lap_time            | datetime            | modification   |
    |:--------------------|:--------------------|:---------------|
    | 2022-06-21 16:08:16 | 2022-06-21 16:08:25 | nan            |
    | 2022-06-21 16:08:24 | 2022-06-21 16:08:33 | added          |
    | 2022-06-21 18:07:12 | 2022-06-21 18:07:21 | added          |
    | 2022-06-21 18:07:12 | 2022-06-21 18:07:21 | added          |
    | 2022-06-21 19:06:25 | 2022-06-21 19:06:29 | nan            |
    | 2022-06-21 19:13:28 | 2022-06-21 19:13:32 | added          |
    | 2022-06-21 20:08:15 | 2022-06-21 20:08:19 | added          |
    | 2022-06-21 20:08:16 | 2022-06-21 20:08:22 | nan            |

    Missing laps have been added, along with the columns modification.

    """

    data = data.copy()
    data = pd.DataFrame(data)

    # treat date columns
    data.datetime = pd.to_datetime(data.datetime)
    data.lap_time = pd.to_datetime(data.lap_time)
    data["day"] = data.datetime.dt.date

    # sort values
    data.sort_values(["segment", "day", "lap", "datetime"], inplace=True)

    # compute laps start and end
    laps_grouped = data.groupby(["segment", "lap"])[["datetime", "lap_id", "dir_veh"]]
    laps = laps_grouped.first().rename(columns={"datetime": "first"})

    data_to_insert = []
    data["modification"] = np.nan

    grouped = data.groupby(
        [constants.PLATE, constants.SEGMENT, constants.SIDE_OF_STREET, "cluster_id"]
    )

    for (_, segment, dir_veh, _), plaque_data in grouped:
        plaque_data.sort_values("lap", inplace=True)

        for i in range(1, plaque_data.shape[0]):
            # check if lap are consecutive
            lap_before = plaque_data.iloc[i - 1][["lap"]].values[0]
            lap_after = plaque_data.iloc[i][["lap"]].values[0]
            lap_time_before = plaque_data.iloc[i - 1][["lap_time"]].values[0]
            lap_time_after = plaque_data.iloc[i][["lap_time"]].values[0]
            day_before = plaque_data.iloc[i - 1].datetime.date()
            day_after = plaque_data.iloc[i].datetime.date()

            # if elapsed time is to much, don't smooth
            if (lap_time_after - lap_time_before).total_seconds() >= max_lap_creation:
                continue

            # time for the car to get to the veh
            time_delta = (
                plaque_data.iloc[i - 1][["datetime"]].values[0]
                - plaque_data.iloc[i - 1][["lap_time"]].values[0]
            )
            # There is a gap in the laps seq, fill it
            if lap_before != lap_after - 1 and day_before == day_after:
                for lap_missing in range(lap_before + 1, lap_after):
                    if laps.loc[(segment, lap_missing), "dir_veh"] != dir_veh:
                        continue
                    try:
                        row_to_insert = plaque_data.iloc[i - 1].copy()
                        row_to_insert["data_index"] = (
                            f"I{lap_missing}_{row_to_insert['data_index']}"
                        )
                        row_to_insert["lap"] = lap_missing
                        row_to_insert["lap_id"] = laps.loc[
                            (row_to_insert["segment"], lap_missing), "lap_id"
                        ]
                        row_to_insert["lap_time"] = laps.loc[
                            (row_to_insert["segment"], lap_missing), "first"
                        ]
                        row_to_insert["datetime"] = (
                            row_to_insert["lap_time"] + time_delta
                        )
                        row_to_insert["modification"] = "added"

                        data_to_insert.append(row_to_insert.to_frame().T)
                    # There is a non temporal a gap in the lap sequence
                    # (i.e. deleted data) : skip
                    except KeyError:
                        pass

        data_to_insert.append(plaque_data)

    data_smoothed = pd.concat(data_to_insert, axis=0)
    data_smoothed.sort_values("datetime", inplace=True)

    return data_smoothed
