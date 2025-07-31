# -*- coding: utf-8 -*-
"""
Created on Wed Jun  9 10:12:27 2021

@author: lgauthier
@author: alaurent
"""
from deprecated import deprecated
import numpy as np
import pandas as pd
import geopandas as gpd


@deprecated(
    reason='Data should be a TrajDataFrame which include to_geodataframe' +
           'method'
)
def df2gdf(
    data: pd.DataFrame,
    lat_col: str = 'lat',
    lng_col: str = 'lng',
    crs: str = 'epsg:4326',
    project_crs: str = 'epsg:32188'
) -> gpd.GeoDataFrame:
    """ Helper function to transform a DataFrame with X, Y values
    to a GeoDataFrame.

    Paramaters
    ----------
    data : pandas.DataFrame
        Data to georeference.
    lat_col : string (Default: 'lat')
        Column name of Ys values for (X,Y) points.
    lng_col : string (Default: 'lng')
        Column name of Xs values for (X,Y) points.
    crs : string (Default: 'epsg:4326')
        Projection of the points in data. Must be a valid CRS format.
    project_crs : string (Default: 'epsg:32188')
        Projection fo the points in the result GeoDataFrame. Must be a valid
        CRS format.

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame of the input data in projection `project_crs`.
    """
    data = data.copy()

    geom = gpd.points_from_xy(data[lng_col], data[lat_col])
    gdf = gpd.GeoDataFrame(data, geometry=geom, crs=crs)

    return gdf.to_crs(project_crs)


def class_dist_computation(
    trips: pd.DataFrame,
    step: float = 0.1,
    rounding: int = 0,
    null_val: int = -1
) -> list[float]:
    """ Compute the distance quantiles of the trips

    Parameters
    ----------
    trips : pandas.DataFrame
        Enhance lapi data with computation of origins.
    step : float
        Quantile steps
    null_val : int or str
        Values of null values, if there is.

    Returns
    -------
    list[float]
        Quantile of distance for each step.

    Raises
    ------
    ValueError
        trips data must contain dist_ori_m column.
    """
    trips = trips.copy()

    if 'dist_ori_m' not in trips.columns:
        raise ValueError(
            'Distance between immo and origin must be computed first.'
        )

    # remove null values
    trips = trips[trips.dist_ori_m != null_val]

    # compute distance gap
    dist_list = [trips.dist_ori_m.min(),]
    dist_val = trips.sort_values('dist_ori_m')['dist_ori_m'].values
    shape_dist = dist_val.shape[0]
    for i in range(1, int(100/(100*step)) + 1):
        idx = np.ceil(shape_dist*step*i).astype(int)
        if idx == shape_dist:
            idx -= 1
        dist_list.append(dist_val[idx])

    dist_list = np.array(dist_list)

    return list(np.round(dist_list/1000, rounding))


def stats_for_dist_class(
    trips: pd.DataFrame,
    class_dist: list[float] = [0, 0.25, 0.5, 1.5, 3, 4.5, 6, 9, 12, 20, np.inf]
) -> pd.DataFrame:
    """ Compute trip distribution by classe distance.

    Parameters
    ----------
    trips : pandas.DataFrame
        Enhance lapi data with computation of origins.
    class_dist : float iterbale
        Class distances in km

    Returns
    -------
    pandas.DataFrame
        Per class : Count immo, percent immo, cumsum immo and
        percent cumsum immo
    """
    trips = trips.copy()

    class_str = [f'<{i} km' for i in class_dist[1:-1]] + ['autres']
    count, _ = np.histogram(trips['dist_ori_m'], bins=class_dist)
    df = pd.DataFrame(
        index=class_str,
        data=zip(
            count,
            np.round(count/count.sum()*100, 0).astype(int),
            np.cumsum(count),
            np.round(np.cumsum(count)/count.sum()*100, 0).astype(int)
        ),
        columns=['nbr_class', 'prc_class', 'nbr_cumsum', 'prc_cumsum']
    )

    return df


def prov_by_region(
    trips: pd.DataFrame,
    discretisation: gpd.GeoDataFrame,
    local_crs: str = 'epsg:32188'
) -> pd.DataFrame:
    """ Compute trip distribution by regions.

    Parameters
    ----------
    trips : pandas.DataFrame
        Enhance lapi data with computation of origins.
    discretisation : geopandas.GeoDataFrame
        Shapes of the regions discretisation. Must have a 'Label' column.

    Returns
    -------
    pandas.DataFrame
        Count and percentage of immo origins per region.

    Raises
    ------
    ValueError
        trips data should contains `ori_lat` column.
    ValueError
        discretisation data should contains `Label` column.
    ValueError
        trips data should contains `is_com` column.
    """
    trips = trips.copy()
    discretisation = discretisation.copy()

    if 'ori_lat' not in trips.columns:
        raise ValueError('Origins of immo must be computed first.')

    if 'Label' not in discretisation.columns:
        raise ValueError('Discretisation must have a Label column.')

    if 'is_com' not in trips.columns:
        raise ValueError('Plaque must have a type column (i.e. "is_com").')

    # trips origine to GDF
    trips_gdf = df2gdf(trips, 'ori_lat', 'ori_lng', project_crs=local_crs)

    # harmonize CRS
    discretisation.to_crs(local_crs, inplace=True)

    # Python Kernel dies for an obscure reason if the spatial join is
    # done after the time_slot filtering.

    # spatial join with shapefile
    trips = gpd.sjoin(discretisation,
                      trips_gdf,
                      predicate='contains',
                      how='inner')

    # count total origins
    count_by_reg = discretisation.merge(
        trips.pivot_table(
            index='Label',
            aggfunc='size'
        ).to_frame('nb_reg'),
        on='Label',
        how='left'
    ).fillna(0)

    # count commercials vehicule origins
    count_by_reg = count_by_reg.merge(
        trips[trips.is_com].pivot_table(
            index='Label',
            aggfunc='size'
        ).to_frame('nb_com_reg'),
        on='Label',
        how='left'
    ).fillna(0)

    # count personal vehicule origins
    count_by_reg['nb_pers_reg'] = count_by_reg.nb_reg - count_by_reg.nb_com_reg

    # compute percentage
    count_by_reg['prc_reg'] = (count_by_reg.nb_reg /
                               count_by_reg.nb_reg.sum() * 100)
    count_by_reg['prc_com_reg'] = (count_by_reg.nb_com_reg /
                                   count_by_reg.nb_reg.sum() * 100)
    count_by_reg['prc_pers_reg'] = (count_by_reg.prc_reg -
                                    count_by_reg.prc_com_reg)

    # clean
    count_by_reg = count_by_reg.rename(columns={'Label': 'reg'})
    cols_to_rm = discretisation.columns.to_list()
    trips.reset_index(drop=True, inplace=True)
    trips.drop(columns=['index_right']+cols_to_rm, inplace=True)
    trips = df2gdf(trips, 'ori_lat', 'ori_lng', project_crs=local_crs)

    return trips, count_by_reg
