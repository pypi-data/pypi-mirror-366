"""Module providing graph operation for Geobase GeoDataFrame"""

import itertools
import warnings

import numpy as np
import networkx as nx
import osmnx as ox
import momepy
import pandas as pd
import geopandas as gpd
import pyproj

from lapin import constants
from lapin.tools.geom import azimuth, line_azimuth

ROAD_CLASS_MAPPING = {
    0: 'residential',
    1: 'pedestrian',
    2: 'service',
    3: 'service',
    4: 'service',
    5: 'tertiary',
    6: 'secondary',
    7: 'primary',
    8: 'motorway',
    9: 'motorway'
}


def construct_graph(lines: gpd.GeoDataFrame,
                    limits: gpd.GeoDataFrame = None,
                    crs: str = constants.DEFAULT_CRS) -> nx.Graph:
    """
    Converts a serie of geometric lines into a graph with nodes and edges.

    Parameters
    ----------
    lines : gpd.GeoDataFrame
        The set of lines to transform.
    limits : gpd.GeoDataFrame, optional
        Optional boundaries to select a subset of the lines with (lines that
        intersected the boundaries and kept whole). The default is None.
    crs : str, optional
        The crs in which the objects in `lines` are projected. The default is
        DEFAULT_CRS (see tools.geom).

    Returns
    -------
    graph : nx.Graph
        The graph object.

    Raises
    ------
    ValueError: CRS must be a string or pyproj.CRS
    """

    lines = lines.copy()
    lines = lines.to_crs(crs)

    if isinstance(crs, str):
        crs = pyproj.CRS.from_string(crs)
    if not isinstance(crs, pyproj.CRS):
        raise ValueError("CRS should be string or pyproj.CRS")

    if isinstance(limits, gpd.GeoDataFrame):
        columns = lines.columns
        limits = limits.copy()

        # 1 - project to same crs
        limits = limits.to_crs(crs)

        # 2 - create graph
        lines = gpd.sjoin(
            left_df=lines,
            right_df=limits,
            predicate='intersects',
            how='inner'
        ).reset_index()

        # 3 - remove duplicates created by join
        lines = lines[columns].drop_duplicates().reset_index(drop=True)

    # prepare data
    index_names = lines.index.names
    lines = lines.reset_index()

    # set tolerance to 10 unit (meters), and handle degree CRS
    tolerance = 10
    if (
        isinstance(crs, pyproj.CRS) and
        crs.coordinate_system.axis_list[0].unit_name == 'degree'
    ):
        tolerance = 10 / constants.EARTH_RADIUS

    # needs pygeos
    lines.geometry = momepy.close_gaps(lines, tolerance)

    # re-index
    index_names = index_names if len(index_names) > 1 else index_names[0]
    if index_names:
        lines = lines.set_index(index_names)
    else:
        lines = lines.set_index('index')

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        graph = momepy.gdf_to_nx(lines, approach='primal')

    return graph


def get_segment_intersection_name(graph: nx.Graph, seg_id: int,
                                  seg_col: str = 'segment',
                                  col_name: str = 'Rue') -> tuple[str, str]:
    """
    Query the name of the intersections (as street1, street2) from a road
    segment taken in a graph built using the construct_graph function

    Parameters
    ----------
    graph : nx.Graph
        The graph to search.
    seg_id : int
        The id from the segment to document.
    seg_col : str, optional
        The name of the attribute in which the edges names are stored.
        The default is 'segment'.
    col_name : str, optional
        The name of the attribute in which the node names are stored.
        The default is 'Rue'.

    Returns
    -------
    tuple[str, str]
        The name of the two intersecting streets, in the edge's vector
        direction.

    """
    _, edges = momepy.nx_to_gdf(graph)

    try:
        nodes_start = edges.set_index(seg_col).loc[seg_id, 'node_start']
        nodes_end = edges.set_index(seg_col).loc[seg_id, 'node_end']
        street_name = edges.set_index(seg_col).loc[seg_id, col_name]
    except KeyError:
        return np.repeat('Segment not found', 2)
    try:
        rfrom = edges[
            ((edges.node_start == nodes_start) |
             (edges.node_end == nodes_start)) &
            (edges[col_name] != street_name)
        ][col_name].unique()[0]
    except IndexError:
        rfrom = "N/A"

    try:
        rto = edges[
            ((edges.node_start == nodes_end) |
             (edges.node_end == nodes_end)) &
            (edges[col_name] != street_name)
        ][col_name].unique()[0]
    except IndexError:
        rto = "N/A"

    return rfrom, rto


def convert_geobase_to_osmnx(gdf_network: gpd.GeoDataFrame,
                             traffic_dir: bool = True) -> nx.MultiGraph:
    """Convert a geobase to a OSMNX graph

    Parameters
    ----------
    gdf_network : gpd.GeoDataFrame
        Geobase

    Returns
    -------
    nx.MultiGraph
            Geobase graph
    """
    gdf_network = gdf_network.copy()
    gdf_network = gdf_network.to_crs(constants.MONTREAL_CRS)

    if traffic_dir:
        # reverse geometry of non_directional street numerized the oposite ways
        mask = gdf_network[constants.TRAFFIC_DIR] == -1
        gdf_network.loc[mask,
                        'geometry'] = gdf_network.loc[mask,
                                                      'geometry'].reverse()
    else:
        gdf_network[constants.TRAFFIC_DIR] = False

    # convert to Universal and save road length before
    gdf_network['sv_length'] = gdf_network.geometry.length
    gdf_network = gdf_network.to_crs(constants.DEFAULT_CRS)

    # convert to networkx graph
    max_id_trc = gdf_network[constants.SEGMENT].max()

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        net = momepy.gdf_to_nx(
            gdf_network,
            'primal',
            directed=True,
            oneway_column=constants.TRAFFIC_DIR
        )

    net = nx.convert_node_labels_to_integers(
        net,
        first_label=max_id_trc + 1,
        label_attribute='xy'
    )

    # get data
    nodes_idx, nodes_data = zip(*net.nodes(data=True))
    u, v, edges_data = zip(*net.edges(data=True))

    # transform edges to osrmx style
    gdf_edges = gpd.GeoDataFrame(
        data=edges_data,
        index=pd.MultiIndex.from_tuples(
            tuples=list(zip(*[u, v, itertools.repeat(0)])),
            names=['u', 'v', 'key']
        ),
        crs=constants.DEFAULT_CRS
    )

    gdf_edges.rename(columns={
        constants.SEGMENT: 'uniqueid',
        constants.TRAFFIC_DIR: 'oneway',
        'sv_length': 'length',
        constants.ROAD_NAME: 'name',
        'CLASSE': 'highway'
    }, inplace=True)

    gdf_edges['reversed'] = gdf_edges.oneway == -1
    gdf_edges['oneway'] = gdf_edges.oneway.astype(bool)
    gdf_edges['highway'] = gdf_edges.highway.map(ROAD_CLASS_MAPPING)
    gdf_edges['ref'] = np.nan
    gdf_edges['width'] = np.nan
    gdf_edges['lanes'] = 1
    gdf_edges['uniqueid'] = gdf_edges.uniqueid.astype(np.int64)

    gdf_edges = gdf_edges[['uniqueid', 'lanes', 'name', 'highway', 'oneway',
                           'reversed', 'length', 'geometry', 'ref', 'width']]
    gdf_edges.sort_index(inplace=True)

    # tranform nodes to networkx graph
    df_nodes = pd.DataFrame(
        data=nodes_data,
        index=pd.Index(nodes_idx, name='osmid')
    )

    df_nodes['x'] = df_nodes.apply(lambda x: x.xy[0], axis=1)
    df_nodes['y'] = df_nodes.apply(lambda x: x.xy[1], axis=1)
    gdf_nodes = gpd.GeoDataFrame(
        data=df_nodes,
        geometry=gpd.points_from_xy(df_nodes.x, df_nodes.y),
        crs=constants.DEFAULT_CRS
    )

    for (u, v, k), row in gdf_edges.iterrows():
        node1 = list(gdf_nodes.loc[u, 'geometry'].coords)[0]
        node2 = list(gdf_nodes.loc[v, 'geometry'].coords)[0]
        edge_az = azimuth(node1, node2)
        road_az = line_azimuth(row['geometry'])

        is_reversed = False if np.abs(edge_az - road_az) < 10 else True
        gdf_edges.loc[(u, v, k), 'reversed'] = is_reversed

    gdf_edges.sort_index(inplace=True)
    gdf_nodes.sort_index(inplace=True)

    net_osm = ox.graph_from_gdfs(gdf_nodes=gdf_nodes, gdf_edges=gdf_edges)

    return net_osm


def save_geobase_to_osm(roads: gpd.GeoDataFrame, path: str,
                        traffic_dir: bool = False) -> None:
    """ Save a geobase to a osm xml format

    Parameters
    ----------
    roads : gpd.GeoDataFrame
        geobase describing each roads
    traffic_dir : bool
        Set the edge graph as unidirected or not
    """

    ox.settings.all_oneway = True

    net_osm = convert_geobase_to_osmnx(roads, traffic_dir=traffic_dir)

    ox.save_graph_xml(net_osm, path)
