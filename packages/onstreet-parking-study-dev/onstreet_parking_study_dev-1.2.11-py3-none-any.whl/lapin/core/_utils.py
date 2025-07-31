""" Utils for lapin.core
"""
import typing
import itertools
import pandas as pd
import geopandas as gpd

from lapin import constants
from lapin.core import TrajDataFrame
from lapin.tools.utils import IncompleteDataError


def side_of_street_of_vehicule(veh_data: TrajDataFrame):
    """ Compute all the potential side of street that a vehicule could have
    scan.  This assume that every vehicules has both, right and left cameras
    open. If this is not the case, see
    method RoadNetwork.filter_veh_side_of_street.

    Parameters
    ----------
    veh_data : TrajDataFrame
       GPS data of every vehicule during the study period.

    Return
    ------
    veh_data: TrajDataFrame
        Vehicule data with columns 'side_of_street' added.

    Raises
    ------
    MissingDataWarning
        Data should contain the pre-computed 'segment' column. This is a
        results from enhancement.preprocessing.mapmatch function.
    MissingDataWarning
        Data should contain the pre-computed ''traffic-dir' column. This is
        a results of merging roadnetwork information with veh data.

    See Also
    --------
    RoadNetwork.filter_veh_side_of_street :
        match data with camera activation.
    enhancement.preprocessing.mapmatch :
        derive the road network from bare GPS point.
    """
    if 'segment' not in veh_data.columns:
        raise IncompleteDataError(
            veh_data,
            'segment',
            'side_of_street_of_vehicule'
        )
    if 'traffic_dir' not in veh_data.columns:
        raise IncompleteDataError(
            veh_data,
            'traffic_dir',
            'side_of_street_of_vehicule'
        )
    if 'dir_veh' not in veh_data.columns:
        raise IncompleteDataError(
            veh_data,
            'dir_veh',
            'side_of_street_of_vehicule'
        )

    veh_data = veh_data.copy()
    veh_data.drop(columns='side_of_street', inplace=True, errors='ignore')
    veh_data_mul_dir = veh_data[veh_data.traffic_dir == 0].copy()
    veh_data_uni_dir = veh_data[veh_data.traffic_dir != 0].copy()

    # street parking is always on the right side on bi-directional street.
    veh_data_mul_dir['side_of_street'] = 1 * veh_data_mul_dir['dir_veh']

    # we can scan both direction on uni-directional street.
    veh_data_uni_dir['side_of_street'] = 1
    veh_data_otr_sid = veh_data_uni_dir.copy()
    veh_data_otr_sid['side_of_street'] = -1

    return pd.concat([veh_data_mul_dir,
                      veh_data_uni_dir,
                      veh_data_otr_sid], ignore_index=True, axis=0)


def create_network_config(
    roads: gpd.GeoDataFrame,
    uuid_list: list[str],
    zone: gpd.GeoDataFrame = None,
    desagregated_street: list[str] = None
) -> pd.DataFrame:
    """_summary_

    Parameters
    ----------
    roads : gpd.GeoDataFrame
        _description_
    uuid_list : list[str]
        _description_
    zone : gpd.GeoDataFrame, optional
        _description_, by default None
    desagregated_street : list[str], optional
        _description_, by default None

    Returns
    -------
    pd.DataFrame
        _description_
    """
    roads = roads.copy()

    if isinstance(zone, gpd.GeoDataFrame):
        roads = gpd.sjoin(roads, zone.to_crs(roads.crs), predicate='within')

    roads_seg = roads[constants.SEGMENT].values
    side_of_street = [1, -1]
    aggregate = roads[constants.TRAFFIC_DIR].map(
        {-1: True, 1: True, 0: False}
    ).values
    roads['aggregate'] = aggregate

    nt_config = pd.DataFrame(
        data=list(itertools.product(roads_seg, side_of_street, uuid_list)),
        columns=[constants.SEGMENT, constants.SIDE_OF_STREET, constants.UUID]
    )
    nt_config = nt_config.join(
        other=roads.set_index(constants.SEGMENT)[['aggregate',
                                                  constants.ROAD_NAME]],
        on='segment'
    )

    nt_config.loc[
        nt_config[constants.ROAD_NAME].isin(desagregated_street),
        'aggregate'
    ] = False

    return nt_config


def prepare_data_before_export(
    data: pd.DataFrame,
    street_geom: gpd.GeoDataFrame,
    weight: pd.DataFrame = pd.DataFrame(
        columns=[constants.SEGMENT, constants.SIDE_OF_STREET]
    ),
    zero_weight_replace: object = 'Aucune place',
) -> pd.DataFrame:
    """ Attach geometry and use weight to dissern between real zeros
    and weight induced zeros.

    Parameters
    ----------
    data : pd.DataFrame
        _description_
    street_geom : gpd.GeoDataFrame
        _description_
    weight: pd.DataFrame, optional
        Weight for data, by default empty DataFrame
    zero_weight_replace: object, optional
        Value to set in data when weight == 0, by default 'Aucune place'

    Raises
    ------
    ValueError
        data and weight must have the same shape.
    """
    data = data.copy()
    weight = weight.copy()

    if (
        constants.SEGMENT not in data.columns or
        constants.SIDE_OF_STREET not in data.columns
    ):
        raise IncompleteDataError(
            data,
            [constants.SEGMENT, constants.SIDE_OF_STREET],
            data.columns
        )
    if (
        constants.SEGMENT not in weight.columns or
        constants.SIDE_OF_STREET not in weight.columns
    ):
        raise IncompleteDataError(
            weight,
            [constants.SEGMENT, constants.SIDE_OF_STREET],
            weight.columns
        )

    data = data.set_index([constants.SEGMENT,
                           constants.SIDE_OF_STREET])
    weight = weight.set_index([constants.SEGMENT,
                               constants.SIDE_OF_STREET])

    # for human, we mix float and string value
    cols = [c for c in data.columns if data[c].dtype == float]
    col_dtypes = {c: object for c in cols}
    data = data.astype(col_dtypes)

    # no geometry
    if isinstance(data, gpd.GeoDataFrame):
        return data

    if not isinstance(street_geom, gpd.GeoDataFrame):
        return data

    if not weight.empty and weight.shape != data.shape:
        raise ValueError('DataFrame weight and data shapes differ.')

    if not weight.empty:
        data = data.where(weight != 0, zero_weight_replace)

    if 'geometry' not in data.columns:
        data = data.join(
            street_geom['geometry'],
            how='right',
            on=['segment', 'side_of_street']
        )
        # if there is no entry, no vehicule has been on this road
        if not weight.empty:
            data.loc[
                data[cols].isna().all(axis=1),
                cols
            ] = 'Non parcourue'

        else:
            data.loc[
                data[cols].isna().all(axis=1),
                'restrictions'
            ] = 'Non parcourue'

        data = gpd.GeoDataFrame(data, crs=street_geom.crs)

    return data


def json_keys_2_int(x_dict: dict | typing.Any) -> dict:
    """Transform every key of dict to int if possible

    Parameters
    ----------
    x_dict : dict
        dict to transform

    Returns
    -------
    dict
        key transformed to int when possible
    """
    if isinstance(x_dict, dict):
        res = {}
        for k, v in x_dict.items():
            try:
                res[int(k)] = json_keys_2_int(v)
            except ValueError:
                res[k] = json_keys_2_int(v)
        return res
    return x_dict
