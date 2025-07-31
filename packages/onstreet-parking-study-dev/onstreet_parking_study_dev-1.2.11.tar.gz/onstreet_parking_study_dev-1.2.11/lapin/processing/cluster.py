"""This module provide clustering functions to enhance data."""

from typing import Callable
import multiprocessing as mp
from deprecated import deprecated
import numpy as np
import pandas as pd

from shapely.geometry import (
    Point,
    MultiPoint,
)
from geopy.distance import great_circle
from sklearn.cluster import DBSCAN

from lapin.tools.utils import IncompleteDataError
from lapin.core import TrajDataFrame, LprDataFrame
from lapin import constants


def get_point_med(data: pd.Series) -> Point:
    """Find the median point of a list of point.

    Parameters
    ----------
    data : pandas.Series
        Series of list of longitude, latitude.

    Returns
    -------
    shapely.Point
        Median point.
    """
    if data.shape[0] <= 1:
        return Point(data.iloc[0])

    data_point = data.values
    return MultiPoint(data_point).centroid


def _dbscan_plate_clustering(
    plate_data: pd.DataFrame,
    eps: float,
    min_samples: int = 1,
    metric: str = "euclidean",
) -> tuple[pd.DataFrame, list[int]]:
    """Clustering plates with DBSCAN.

    Parameters
    ----------
    plate_data : pd.DataFrame
        Plates positions data.
    eps : float
        DBSCAN eps param.
    min_samples : int, optional
        DBSCAN min_samples param, by default 1.
    metric : str, optional
        DBSCAN metric param, by default 'euclidean'.

    Returns
    -------
    pandas.DataFrame
        Median point of clusterized plates position. Add columns
        'lat_s' and 'lng_s'.
    list[int]
        cluster of each plate
    """
    plate_data = plate_data.copy()

    dbsc = DBSCAN(eps=eps, min_samples=min_samples, metric=metric).fit(
        plate_data[["lng", "lat"]]
    )

    cluster = dbsc.labels_

    plate_data["cluster_id"] = cluster
    plate_data["lnglat"] = plate_data[["lng", "lat"]].apply(list, axis=1)
    plate_data["pt_smooth"] = plate_data.groupby("cluster_id")["lnglat"].transform(
        get_point_med
    )
    plate_data["lat_s"] = plate_data.apply(lambda x: x.pt_smooth.y, axis=1)
    plate_data["lng_s"] = plate_data.apply(lambda x: x.pt_smooth.x, axis=1)

    plate_data.drop(columns=["lnglat", "pt_smooth"], inplace=True)

    return plate_data, cluster


@deprecated(reason="Method does not work as intented. Please use DBSCAN alternative.")
def _in_house_clustering(
    plate_data: pd.DataFrame, delta: float
) -> tuple[pd.DataFrame, list[int]]:
    """In house clusterization method.

    CAREFULL : This method il flawed and doesn't work as intended.

    Parameters
    ----------
    plate_data : pd.DataFrame
        Plates positions data.
    delta : float
        Max distance between two plates.

    Returns
    -------
    pandas.DataFrame
        Median point of clusterized plates position. Add columns
        'lat_s' and 'lng_s'.
    list[int]
        cluster of each plate
    """
    plate_data = plate_data.copy()
    plate_data.sort_values(["lap", "datetime"], inplace=True)
    # generate median point for this cluster of vehicule
    median_point = plate_data[["lng", "lat"]].iloc[0].values
    new_points_list = []
    cluster = [0]

    for i in range(1, plate_data.shape[0]):
        dist = great_circle(
            median_point[::-1], plate_data.iloc[i][["lat", "lng"]].values
        ).m

        if dist <= delta:
            # update median point for cluster
            median_point = MultiPoint(
                [Point(median_point), Point(plate_data[["lng", "lat"]].iloc[i])]
            ).centroid.xy
            median_point = np.array(median_point).flatten()

            # extend cluster with this park
            cluster.append(cluster[-1])

        # Point not in cluster
        else:
            # create new cluster
            cluster.append(cluster[-1] + 1)
            # append previous cluster median point
            new_points_list.append(median_point)
            # select new median point
            median_point = plate_data[["lng", "lat"]].iloc[i].values

    new_points_list.append(median_point)  # append last point cluster

    # set cluster info
    plate_data["cluster_id"] = cluster
    point_smooth = [Point(new_points_list[c]) for c in cluster]
    plate_data["lat_s"] = [point.y for point in point_smooth]
    plate_data["lng_s"] = [point.x for point in point_smooth]

    return plate_data, cluster


def _default_pos_smoothing(func: Callable, df: LprDataFrame, func_args: dict = None):
    plaque_data, cluster = func(df, **func_args)

    point_on_street_smooth = plaque_data.groupby("cluster_id")["point_on_segment"].agg(
        "mean"
    )
    plaque_data["point_on_segment_s"] = [
        point_on_street_smooth[cluster] for cluster in cluster
    ]

    return plaque_data


def park_pos_smoothing(
    data: LprDataFrame, delta: int = 5, dbscan: bool = True
) -> TrajDataFrame:
    """Clean geographic position of plaque sighted in the data.

    Cluster consecutive observations of same plaque sighted that are close
    (<delta).  New geographic point for clustered plaque is determined as the
    median of all readings clustered.

    Parameters
    ----------
    data: LprDataFrame
        Plates position data.
    delta: int, optional
        Distance in meters for clustering, dy default 5.
    dbscan: bool, optional
        Use dbscan to clusterise plates.

    Returns
    -------
    data: pd.DataFrame.
        Ehancer data, cleaned by clustering process.

    Raises
    ------
    IncompleteDataError
        data must have columns plaque
    IncompleteDataError
        data must have columns side_of_street
    IncompleteDataError
        data must have columns segment
    IncompleteDataError
        data must have columns lap
    IncompleteDataError
        data must have columns datetime
    """
    data = data.copy()

    if constants.PLATE not in data.columns:
        raise IncompleteDataError(data, constants.PLATE, "in plate postion smoothing.")
    if constants.SEGMENT not in data.columns:
        raise IncompleteDataError(
            data, constants.SEGMENT, "in plate postion smoothing."
        )
    if constants.SIDE_OF_STREET not in data.columns:
        raise IncompleteDataError(
            data, constants.SIDE_OF_STREET, "in plate postion smoothing."
        )
    if "lap" not in data.columns:
        raise IncompleteDataError(data, "lap", "in plate postion smoothing.")
    if constants.DATETIME not in data.columns:
        raise IncompleteDataError(
            data, constants.DATETIME, "in plate postion smoothing."
        )

    # treat date columns
    data[constants.DATETIME] = pd.to_datetime(data[constants.DATETIME])

    data.sort_values(
        [
            constants.PLATE,
            constants.SEGMENT,
            constants.SIDE_OF_STREET,
            "lap",
            constants.DATETIME,
        ],
        inplace=True,
    )
    grouped = data.groupby(
        [
            constants.PLATE,
            constants.SEGMENT,
            constants.SIDE_OF_STREET,
            data[constants.DATETIME].dt.date,
        ]
    )

    # default function args
    if dbscan:
        func = _dbscan_plate_clustering
        f_args = {"eps": delta, "min_samples": 1, "metric": "euclidean"}
    else:
        func = _in_house_clustering
        f_args = {
            "delta": delta,
        }

    # iterate over the dataframe
    results = []
    save_partial_frame = results.append
    with mp.Pool() as pool:
        for _, plaque_data in grouped:
            save_partial_frame(
                pool.apply_async(
                    _default_pos_smoothing,
                    args=(
                        func,
                        plaque_data,
                        f_args,
                    ),
                )
            )

        data_smoothed = pd.concat([result.get() for result in results], axis=0)

        return data_smoothed
