"""Module made to merge vehicule position data to LPR readings on study's
streets.

Provide class VisitedSegment and RoadNetwork and function
side_of_street_of_vehicule.
"""

from __future__ import annotations
import itertools
import logging
from typing import TypeAlias
from dataclasses import dataclass, field
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely import LineString, MultiLineString

from lapin import constants
from lapin.core import TrajDataFrame, LprDataFrame
from lapin.core.geobase_network import RoadNetwork, RoadNetworkDouble
from lapin.core import Curbs
from lapin.tools.utils import MissingDataWarning
from lapin.models import occup, rempla, basic
from lapin.core._utils import prepare_data_before_export, side_of_street_of_vehicule
from lapin.models.reassignement import SpotReassignement

VehiculeConf: TypeAlias = dict[str, dict[int, list[dict[str, str]]]]
logger = logging.getLogger(__name__)


@dataclass
class Segment:
    """Basic structure of a Segment"""

    id: int
    side_of_street: int
    traffic_dir: int
    geometry: LineString | MultiLineString = None

    _crs = None

    def merge(self, other: Segment) -> Segment:
        """Merge two side of street together

        Parameters
        ----------
        other : Segment
            Other side of street

        Returns
        -------
        Segment
            Merged segment

        Raises
        ------
        ValueError
            Segment id should be the same
        ValueError
            Side of street should be opposed
        """
        if self.id != other.id:
            raise ValueError("Segment id should be the same.")
        if self.side_of_street != -(other.side_of_street):
            raise ValueError("Side of street should be opposed.")

        self.side_of_street = 0
        if self.geometry and other.geometry:
            self.geometry = MultiLineString([self.geometry, other.geometry])
        if not self.geometry and other.geometry:
            self.geometry = other.geometry

        return self

    def to_json(self) -> dict:
        """Retrun an JSON representation of the Segment

        Returns
        -------
        dict
        """

        segment_json = {}

        segment_json[constants.SEGMENT] = self.id
        segment_json[constants.SIDE_OF_STREET] = self.side_of_street
        segment_json["traffic_dir"] = self.traffic_dir
        if self.geometry:
            segment_json["geometry"] = self.geometry

        return segment_json

    @property
    def crs(self) -> str:
        """Return CRS of geometry"""
        return self._crs

    @crs.setter
    def crs(self, crs_value: str):
        self._crs = crs_value

    @property
    def unique_id(self) -> int:
        if self.side_of_street >= 0:
            return self.id * 10 + self.side_of_street
        return self.id * 10 + 2


@dataclass
class VisitedSegment:
    """This i a class that represent the combination of
    <segment, side_of_street, veh_id> in a collected area. Each
    VisitedSegment represent the times one vehicule could have
    collected parking instance. Capacity at collected time and
    vehicules count are also present.

    This class is needed to compute accuretly the occupancy of
    each curbs we collected. It help us discern between a road
    where no vehicule were parked on it's curb from a road that
    the vehicule has not collected.
    """

    segment: Segment
    veh_id: str
    time_beg: pd.DatetimeIndex
    time_end: pd.DatetimeIndex
    capacity: list[int]
    veh: list[int]
    plates: list[list[str]]
    regulations: list[str]

    @classmethod
    def from_dataframe(cls, veh_data: TrajDataFrame):
        """Populate a segment with GPS veh data. If there is a road geometry
        associated with the veh_data, specify the crs of the roads inside the
        TrajDataFarme.parameters['roads_crs'] attribute.

        Parameters
        ----------
        veh_data : TrajDataFrame
            GPS data of the vehicule.

        Returns
        -------
        VisitedSegment
            _description_

        Raises
        -----
        MissingDataWarning
            Columns 'lap_time' must be computed prior of the initialization.

        See Also
        --------
        enhancement.processing.compute_lpr_lap_sequences
        """
        seg_id = veh_data[constants.SEGMENT].values[0]
        side_of_street = veh_data[constants.SIDE_OF_STREET].values[0]
        veh_id = veh_data[constants.UUID].values[0]
        traffic_dir = veh_data["traffic_dir"].values[0]

        if "lap_time" not in veh_data.columns:
            raise MissingDataWarning("lap_time")

        if "geometry" in veh_data.columns:
            road_geom = veh_data.geometry.iloc[0]
        else:
            road_geom = None

        veh_data = veh_data.copy()
        veh_data = veh_data.sort_values([constants.UUID, constants.DATETIME])
        veh_data_first = (
            veh_data.groupby(["lap_time"]).first().reset_index().set_index("datetime")
        )
        veh_data_last = (
            veh_data.groupby(["lap_time"]).last().reset_index().set_index("datetime")
        )

        assert veh_data_first.index.is_monotonic_increasing

        if "regulations" in veh_data.columns:
            regulations = veh_data_first.regulations.to_list()
        else:
            regulations = list(itertools.repeat(None, veh_data_first.shape[0]))

        segment = Segment(seg_id, side_of_street, traffic_dir, road_geom)

        if "roads_crs" in veh_data.parameters:
            segment.crs(veh_data.parameters["roads_crs"])

        return cls(
            segment=segment,
            veh_id=veh_id,
            capacity=veh_data_first["capacity"].to_list(),
            time_beg=veh_data_first.index,
            time_end=veh_data_last.index,
            veh=list(itertools.repeat(0, veh_data_first.shape[0])),
            plates=list(itertools.repeat([], veh_data_first.shape[0])),
            regulations=regulations,
        )

    def _chose_lap_when_arrival_and_departure_conflicts(self, lpr_readings):

        if (lpr_readings["start"] == lpr_readings["end"]).all():
            lpr_readings["veh_lap"] = lpr_readings["start"]
            return lpr_readings

        conflicts = lpr_readings[lpr_readings.start != lpr_readings.end].copy()
        conflicts["start_time"] = self.time_beg[conflicts.start]
        conflicts["end_time"] = self.time_end[conflicts.end]

        # Three possible configurations :
        # 1. date is < than end_time and < start_time
        #      date   end_time   start_time
        # ------x--------|        |-----------------
        #
        # 2. date is > than end_time and > start_time
        #             end_time   start_time   date
        # ---------------|        |------------x----
        #
        # 3. date is > than end_time and > start_time
        #         end_time     date      start_time
        # ---------------|      x       |------------

        # 1.
        mask_conf1 = (conflicts.start_time > conflicts.datetime) & (
            conflicts.end_time > conflicts.datetime
        )
        conflicts.loc[mask_conf1, "veh_lap"] = conflicts.end
        # 2.
        mask_conf2 = (conflicts.start_time < conflicts.datetime) & (
            conflicts.end_time < conflicts.datetime
        )
        conflicts.loc[mask_conf2, "veh_lap"] = conflicts.start

        # 3.1.
        mask_conf3_end = (
            (conflicts.start_time > conflicts.datetime)
            & (conflicts.end_time < conflicts.datetime)
            & (
                (conflicts.datetime - conflicts.end_time)
                < (conflicts.start_time - conflicts.datetime)
            )
        )
        conflicts.loc[mask_conf3_end, "veh_lap"] = conflicts.end
        # 3.2.
        mask_conf3_start = (
            (conflicts.start_time > conflicts.datetime)
            & (conflicts.end_time < conflicts.datetime)
            & (
                (conflicts.datetime - conflicts.end_time)
                >= (conflicts.start_time - conflicts.datetime)
            )
        )
        conflicts.loc[mask_conf3_start, "veh_lap"] = conflicts.start

        # resolve conflicts
        lpr_readings.loc[(lpr_readings.start != lpr_readings.end), "start"] = (
            conflicts.veh_lap
        )
        lpr_readings.loc[(lpr_readings.start != lpr_readings.end), "end"] = (
            conflicts.veh_lap
        )

        # clean columns
        lpr_readings["veh_lap"] = lpr_readings["start"]
        lpr_readings.drop(columns=["start", "end"], inplace=True)

        return lpr_readings

    def filter(self, vehicules_conf: VehiculeConf):
        """Filter the side of street that could be rich by the vehicule but the
        camera was setted to off.

        Parameters
        ----------
        vehicules_conf : VehiculeConf
            Configuration of active camera for each vehicules, each periods.

        Example
        -------
        >>> print(vehiciles_conf)
            {
            'compact001': {
                1  : [{'from': '2024-06-25 00:00:00',
                       'to':'2024-07-10 23:59:59'}],
                -1 : [{'from': '2024-06-27 00:00:00',
                       'to': '2024-07-10 23:59:59'}]
            },
            'compact002': {
                1  : [{'from': '2024-06-27 00:00:00',
                       'to': '2024-07-10 23:59:59'}],
                -1 : [{'from': '2024-06-25 00:00:00',
                       'to':'2024-07-10 23:59:59'}]
            },
            'compact003': {
                1 : [{'from': '2024-06-25 00:00:00',
                      'to':'2024-07-10 23:59:59'}],
                -1: [{'from': '2024-06-25 00:00:00',
                      'to':'2024-07-10 23:59:59'}]
            }}

        """
        for uuid, conf_sides in vehicules_conf.items():
            if uuid != self.veh_id:
                continue
            for side, dates in conf_sides.items():
                if side != (self.segment.traffic_dir * self.segment.side_of_street):
                    continue
                mask = np.full(self.time_beg.shape, False, dtype=bool)
                for date in dates:
                    append_mask_value = (self.time_beg > date["from"]) & (
                        self.time_end < date["to"]
                    )
                    mask = mask | append_mask_value
                self.veh = list(np.array(self.veh)[mask])
                self.capacity = list(np.array(self.capacity)[mask])
                self.time_beg = self.time_beg[mask]
                self.time_end = self.time_end[mask]
                self.plates = list(itertools.compress(self.plates, mask))
                self.regulations = list(itertools.compress(self.regulations, mask))

    def merge_lpr_readings(self, lpr_reading: LprDataFrame) -> LprDataFrame:
        """Merge vehicule passage with plates recorded on a VisitedSegment.

        Parameters
        ----------
        lpr_reading : LprDataFrame
            Licence plates recognition DataFrame.
        """
        if self.time_beg.empty:
            return pd.DataFrame()

        lpr_reading = lpr_reading.copy()

        lap_based_arrival = self.time_beg.get_indexer(
            target=lpr_reading[constants.DATETIME], method="nearest"
        )
        lap_based_departure = self.time_end.get_indexer(
            target=lpr_reading[constants.DATETIME], method="nearest"
        )

        lpr_reading["start"] = lap_based_arrival
        lpr_reading["end"] = lap_based_departure

        lpr_reading = self._chose_lap_when_arrival_and_departure_conflicts(lpr_reading)

        self.veh = np.zeros_like(self.time_beg, dtype=int)
        veh_count = lpr_reading.groupby("veh_lap").size()

        self.veh[veh_count.index] = veh_count.values

        self.plates = list(itertools.repeat([], self.time_beg.shape[0]))
        plates_list = lpr_reading.groupby("veh_lap")[constants.PLATE].agg(list)

        for index, plates in plates_list.items():
            self.plates[index] = plates

        return lpr_reading

    def occup(self) -> list[float]:
        """Compute capacity for this <vehicule ; segment ; side_of_street>

        Returns
        -------
        list[float]
            Occupancy of the street
        """

        capacity = np.array(self.capacity)
        veh_sigh = np.array(self.veh)

        # if there is capacity, then we have passed on the street,
        # but no data were recolted
        veh_sigh = np.nan_to_num(veh_sigh, nan=0)

        occ = np.divide(
            veh_sigh,
            capacity,
            out=np.zeros_like(veh_sigh, dtype=float),
            where=capacity != 0,
        )

        return occ

    def to_json(self) -> dict:
        """Retrun the segment data as json

        Returns
        -------
        dict
            Segment as json
        """

        segment_json = {}
        segment_json.update(self.segment.to_json())

        segment_json[constants.UUID] = self.veh_id
        segment_json["veh_sighted"] = self.veh
        segment_json[constants.CAP_N_VEH] = self.capacity
        segment_json[constants.LAP] = np.arange(self.time_beg.shape[0])
        segment_json[constants.LAP_TIME] = self.time_beg
        segment_json["occ"] = self.occup()
        segment_json[constants.PLATE] = self.plates
        segment_json[constants.CAP_RESTRICTIONS] = self.regulations

        return segment_json

    def get_laps(self) -> pd.DataFrame:
        """_summary_

        Returns
        -------
        pd.DataFrame
            _description_
        """
        laps = np.arange(self.time_beg.shape[0])
        uuid = list(itertools.repeat(self.veh_id, self.time_beg.shape[0]))
        ids = list(itertools.repeat(self.segment.id, self.time_beg.shape[0]))
        side_of_street = list(
            itertools.repeat(self.segment.side_of_street, self.time_beg.shape[0])
        )

        return pd.DataFrame(
            data=list(
                zip(uuid, ids, side_of_street, laps, self.time_beg, self.time_end)
            ),
            columns=[
                constants.UUID,
                constants.SEGMENT,
                constants.SIDE_OF_STREET,
                "lap",
                "start_time",
                "end_time",
            ],
        )

    def merge_sides(self, other: VisitedSegment) -> VisitedSegment:
        """Merge two side of VisitedSegment together.
        Only possible if this is the same tuple <segment, vehicule> with
        opposite side of street.

        Parameters
        ----------
        other : VisitedSegment
            Visited segment to merge

        Returns
        -------
        VisitedSegment
            VisitedSegment updated with 'other' informations.

        Raises
        ------
        ValueError
            Can only merges readings from same vehicule.
        """
        # already computed
        if self.segment.side_of_street == 0:
            return self

        if self.veh_id != other.veh_id:
            raise ValueError("Can only merges readings from same vehicule.")

        self.segment = self.segment.merge(other.segment)
        self.veh = np.array(self.veh) + np.array(other.veh)
        self.capacity = np.array(self.capacity) + np.array(other.capacity)
        self.plates = [
            self.plates[i] + other.plates[i] for i, _ in enumerate(self.plates)
        ]

        def _are_eguals(str1, str2):
            if str1 == str2:
                return str1
            return None

        self.regulations = list(map(_are_eguals, self.regulations, other.regulations))

        return self


@dataclass
class CollectedArea:
    """Collection of VisitedSegment.

    Used to compute occupancy of every collected street of the study area.
    """

    segments: list[VisitedSegment]
    _index_by_segment: dict[int, list[int]] = field(init=False)
    _index_by_uuid: dict[int, list[int]] = field(init=False)
    _sides_of_street_aggregation_performed: bool = field(default=False, init=False)
    _not_visited: gpd.GeoDataFrame = field(
        default_factory=lambda: gpd.GeoDataFrame(
            columns=[constants.SEGMENT, constants.SIDE_OF_STREET, constants.SEG_DB_GIS],
            geometry=constants.SEG_DB_GIS,
            crs="epsg:4326",
        ),
        init=False,
    )

    def __post_init__(self):
        segment_idx = {}
        veh_idx = {}

        for i, vsegment in enumerate(self.segments):

            sos = (
                2
                if vsegment.segment.side_of_street == -1
                else vsegment.segment.side_of_street
            )

            segment_idx_list = segment_idx.get(int(vsegment.segment.id * 10 + sos), [])
            segment_idx_list.append(i)
            segment_idx[int(vsegment.segment.id * 10 + sos)] = segment_idx_list

            veh_idx_list = veh_idx.get(vsegment.veh_id, [])
            veh_idx_list.append(i)
            veh_idx[vsegment.veh_id] = veh_idx_list

        self._index_by_segment = segment_idx
        self._index_by_uuid = veh_idx

    def populate_road_geometry(
        self, roads: RoadNetworkDouble, force_expand: bool = False
    ):
        """Create geometry with RoadNetworkDouble data

        Parameters
        ----------
        roads : RoadNetworkDouble
            Road geometry
        force_expand : bool, optional
            Add all street were no car has passed.
        """
        roads = roads.copy()
        roads = roads.set_index([constants.SEGMENT, constants.SIDE_OF_STREET])
        roads_covered = []
        for vsegment in self.segments:
            id_seg = vsegment.segment.id
            sos = vsegment.segment.side_of_street
            vsegment.segment.geometry = roads.loc[(id_seg, sos), "geometry"]
            vsegment.segment.crs = roads.crs
            roads_covered.append(vsegment.segment.unique_id)
        if force_expand:
            roads = roads.reset_index()
            roads["unique_id"] = roads[constants.SEGMENT] * 10 + roads[
                constants.SIDE_OF_STREET
            ].map({1: 1, -1: 2})
            roads_to_expand = roads[~roads.unique_id.isin(roads_covered)].copy()
            self._not_visited = roads_to_expand[
                [
                    constants.SEGMENT,
                    constants.SIDE_OF_STREET,
                    constants.TRAFFIC_DIR,
                    constants.SEG_DB_GIS,
                ]
            ]

    @classmethod
    def from_dataframe(cls, veh_data: TrajDataFrame, res_h: Curbs):
        """Fill the RoadNetwork collection with the GPS data position of
        each vehicule of the study area.

        Parameters
        ----------
        veh_data : TrajDataFrame
            GPS data position of the vehicules.
        res_h : Curbs
            Regulation model of the study area.

        Returns
        -------
        RoadNetwork
            The collection of VisitedSegment by each vehicules.
        """

        veh_data = veh_data.copy()

        veh_data = side_of_street_of_vehicule(veh_data)

        if veh_data.empty:
            return cls([])

        veh_data["capacity"] = veh_data.apply(
            lambda x: res_h.get_segment_capacity(
                segment=x["segment"],
                side_of_street=x["side_of_street"],
                time=x["lap_time"],
            ),
            axis=1,
        )
        veh_data = veh_data[~veh_data["capacity"].isna()]

        veh_data["regulations"] = veh_data.apply(
            lambda x: res_h.get_segment_regulation_name(
                segment=x["segment"],
                side_of_street=x["side_of_street"],
                time=x["lap_time"],
            ),
            axis=1,
        )

        segments = []
        grouped = veh_data.groupby(
            ["segment", "side_of_street", constants.UUID, "traffic_dir"]
        )
        for (_, side_of_street, _, _), data in grouped:
            if side_of_street == 0:
                segments.append(VisitedSegment.from_dataframe(veh_data=data))
                segments.append(VisitedSegment.from_dataframe(veh_data=data))
            else:
                segments.append(VisitedSegment.from_dataframe(veh_data=data))

        return cls(segments)

    def merge_lpr_readings(self, lpr_readings: LprDataFrame) -> None:
        """Merge the LPR data collected by the vehicules to the
        vehicule trace.

        Parameters
        ----------
        lpr_readings : LprDataFrame
            Plates readings done by all vehicules. Columns UUID, SEGMENT and
            SIDE_OF_STREET must be already computed.
        """

        grouped = lpr_readings.groupby(
            [constants.UUID, constants.SEGMENT, constants.SIDE_OF_STREET]
        )

        merged_lpr = []
        for (uuid, segment, sos), data in grouped:
            seg = self.get(uuid, segment, sos)

            # there is no data that match lpr_readings
            if not seg:
                continue
            else:
                merged_lpr.append(seg.merge_lpr_readings(data))

        return pd.concat(merged_lpr)

    def filter_vehicules_side_of_street(self, vehicules_conf: VehiculeConf) -> None:
        """If camera were turned off during period of time, remove this
        side of street from VisitedSegment.

        Parameters
        ----------
        vehicules_conf : VehiculeConf
            Configuration of camera for each vehicule.

        See Also
        ------
        VisistedSegment.filter : filtering method for a specific VisitedSegment
        """
        for segment in self.segments:
            segment.filter(vehicules_conf)

    def aggregate_side_of_street_unidirectionnal(
        self, network_config: pd.DataFrame
    ) -> None:
        """Aggregate side of street when traffic direction is unidirectional.

        Parameters
        ----------
        network_config : pd.DataFrame
            Specify for every street if we should aggregate side_of_street.
        """
        grouped = network_config.groupby([constants.SEGMENT, constants.UUID])
        for (segment, uuid), sides in grouped:
            segment_left = self.get(uuid, segment, -1)
            segment_right = self.get(uuid, segment, 1)

            # check if there is no data
            if not (segment_left and segment_right):
                continue

            # verify the vehicule has passed on the
            # street at the same times
            same_passages = (
                segment_left.time_beg.shape == segment_right.time_beg.shape
                and (segment_left.time_beg == segment_right.time_beg).all()
            )

            if sides["aggregate"].any() and same_passages:
                segment_left.merge_sides(segment_right)
                self.remove_segment(segment=segment, uuid=uuid, side_of_street=1)

        self._sides_of_street_aggregation_performed = True

    def update_with_config(
        self, network_config: pd.DataFrame, vehicules_conf: VehiculeConf
    ) -> None:
        """Aggregate side of street when traffic direction is unidirectional
        and remove side of street when camera is turned off.

        Parameters
        ----------
        network_config : pd.DataFrame
            Specify for every street if we should aggregate side_of_street.
        vehicules_conf : VehiculeConf
            Specify when camera is turned off.
        """

        self.filter_vehicules_side_of_street(vehicules_conf)

        self.aggregate_side_of_street_unidirectionnal(network_config)

    def get_by_segment(
        self, segment: int, side_of_street: int = None, index_only: bool = False
    ) -> list[VisitedSegment]:
        """Query the RoadNetwork with segment information.

        Parameters
        ----------
        segment : _type_
            ID of the segment.
        side_of_street : _type_, optional
            ID of the side of street, by default None.

        Returns
        -------
        list[VisitedSegment]
            Every VisitedSegment for the combination of segment, side of
            street.
        """
        results = []

        try:
            if side_of_street:
                side_of_street = side_of_street if side_of_street >= 0 else 2
                id_seg = segment * 10 + side_of_street
                if index_only:
                    results = self._index_by_segment[id_seg]
                else:
                    results = [self.segments[i] for i in self._index_by_segment[id_seg]]

            # aggregated
            elif segment * 10 + 0 in self._index_by_segment:
                if index_only:
                    results = self._index_by_segment[segment * 10 + 0]
                else:
                    results = [
                        self.segments[i]
                        for i in self._index_by_segment[segment * 10 + 0]
                    ]

            else:
                id_r = segment * 10 + 1
                id_l = segment * 10 + 2

                right_part = []
                left_part = []

                if id_r in self._index_by_segment:
                    if index_only:
                        right_part = self._index_by_segment[id_r]
                    else:
                        right_part = [
                            self.segments[i] for i in self._index_by_segment[id_r]
                        ]
                if id_l in self._index_by_segment:
                    if index_only:
                        left_part = self._index_by_segment[id_l]
                    else:
                        left_part = [
                            self.segments[i] for i in self._index_by_segment[id_l]
                        ]

                results = right_part + left_part

        except KeyError:
            return []

        return results

    def get_by_uuid(self, uuid: str, index_only: bool = False) -> list[VisitedSegment]:
        """Query the RoadNetwork with vehicule uuid.

        Parameters
        ----------
        uuid : str
            ID of the vehicule.

        Returns
        -------
        list[VisitedSegment]
            Every VisitedSegment explored by vehicule uuid.
        """
        try:
            if index_only:
                return self._index_by_uuid[uuid]
            else:
                return [self.segments[i] for i in self._index_by_uuid[uuid]]
        except KeyError:
            return []

    def remove_segment(self, segment: int, uuid: str, side_of_street: int) -> None:
        """Delete VisitedSegment from collection.

        Parameters
        ----------
        segment : int
            Segment ID.
        uuid : str
            Vehicule ID.
        side_of_street : int
            Side of street ID.

        Raises
        ------
        ValueError
            There is no VisitedSegment with this ID.
        """
        side_of_street = 2 if side_of_street == -1 else side_of_street
        id_seg = segment * 10 + side_of_street
        indx = np.intersect1d(self._index_by_segment[id_seg], self._index_by_uuid[uuid])
        if indx.shape[0] != 1:
            raise ValueError

        self.segments.pop(indx[0])

        # update the index
        self.__post_init__()

    def get(
        self, uuid: str = None, segment: int = None, side_of_street: int = None
    ) -> VisitedSegment | list[VisitedSegment]:
        """_summary_

        Parameters
        ----------
        uuid : _type_, optional
            _description_, by default None
        segment : _type_, optional
            _description_, by default None
        side_of_street : _type_, optional
            _description_, by default None

        Returns
        -------
        VisitedSegment|list[VisitedSegment]
            _description_
        """
        if not (uuid or segment or side_of_street):
            return self.segments
        if not uuid:
            return self.get_by_segment(segment, side_of_street)
        if not segment:
            return self.get_by_uuid(uuid)

        idx_seg = self.get_by_segment(segment, side_of_street, index_only=True)
        idx_uuid = self.get_by_uuid(uuid, index_only=True)

        indx = np.intersect1d(idx_seg, idx_uuid)

        if indx.shape[0] != 1:
            return []

        return self.segments[indx[0]]

    def get_laps(self) -> pd.DataFrame:
        """Get lap for each segment, side_of_street along with start time
        and end time.

        Returns
        -------
        pd.DataFrame
            Laps info.
        """
        res = []
        for segment in self.segments:
            laps = segment.get_laps()
            if laps.empty:
                continue
            res.append(laps)

        lap_df = pd.concat(res)

        lap_df["day"] = lap_df["start_time"].dt.date

        # create continuous lap for each segment, side_of_street, day
        lap_df = lap_df.sort_values(["segment", "side_of_street", "start_time"])
        lap_df["lap"] = lap_df.groupby(["segment", "side_of_street", "day"]).cumcount()

        lap_df = lap_df.set_index(["segment", "side_of_street", "day", "lap"])

        return lap_df

    def to_dataframe(self) -> pd.DataFrame | gpd.GeoDataFrame:
        """Compute the occupancy of each VisitedSegment.

        Returns
        -------
        pandas.DataFrame | geopandas.GeoDataFrame
            Occupancy for each segment, side of streeet, vehicule
            and time a vehicule passed on the street. Geopandas if 'geometry'
            is defined.
        """

        res = []
        for segment in self.segments:
            res.append(segment.to_json())

        occ_df = pd.DataFrame(res)
        # make it a dataframe where each lap is a row
        occ_df = occ_df.explode(
            [
                "veh_sighted",
                constants.CAP_N_VEH,
                constants.LAP_TIME,
                constants.LAP,
                "occ",
                constants.PLATE,
                constants.CAP_RESTRICTIONS,
            ],
            ignore_index=True,
        )

        # get laps
        laps = self.get_laps()
        occ_df.drop(columns="lap", inplace=True)
        occ_df = occ_df.join(
            other=laps.reset_index().set_index(
                [
                    constants.SEGMENT,
                    constants.SIDE_OF_STREET,
                    constants.UUID,
                    "start_time",
                ]
            )[["lap"]],
            on=[
                constants.SEGMENT,
                constants.SIDE_OF_STREET,
                constants.UUID,
                constants.LAP_TIME,
            ],
            how="left",
        )

        # remove empty side of street were we did not collect data
        occ_df = occ_df.dropna(subset=constants.LAP_TIME)

        occ_df[constants.LAP] = occ_df[constants.LAP].astype(np.int64)

        if "geometry" in occ_df.columns:
            crs = self.segments[0].segment.crs
            occ_df = gpd.GeoDataFrame(occ_df, crs=crs)

        return occ_df

    def occupancy_time_aggregation(
        self,
        days: str = "lun-dim",
        timeslot_beg: str = "0h00",
        timeslot_end: str = "23h59",
        freq: str = "30min",
        export_human_readable: bool = False,
        roads: RoadNetwork = None,
    ) -> (
        tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame] | gpd.GeoDataFrame
    ):
        """Compute occupancy time aggregation.

        Parameters
        ----------
        days: str, optional
            days to compute, by default 'lun-ven'
        timeslot_beg : str, optional
            starting hour, by default '0h00'
        timeslot_end : str, optional
            ending hour, by default '23h59'
        freq : str, optional
            analysis frequency, by default '30min'

        Returns
        -------
        pd.DataFrame
            Occupancy
        pd.DataFrame
            Vehicule count
        pd.DataFrame
            Capacity
        pd.DataFrame
            Restrictions
        or
        gpd.GeodataFrame
            Merged result
        """
        occ_df = self.to_dataframe()

        occ, veh, cap, res = occup.occupancy_time_aggregation(
            occ_df, days, timeslot_beg, timeslot_end, freq
        )

        if export_human_readable:
            if not isinstance(roads, RoadNetwork):
                raise ValueError(
                    "You must pass a instance of RoadNetwork "
                    + "when exporting to human readable."
                )
            data_merged = occup.merge_occupancy_capacity_vehicule(
                occ_hr=occ, cap_hr=cap, veh_hr=veh, res_hr=res
            )
            return occup.street_hourly_formater(
                data=data_merged, segments=roads.human_readable, hour_column="hour"
            )

        return occ, veh, cap, res

    def occupancy_by_regions(
        self,
        regions: pd.DataFrame,
        days: str = "lun-dim",
        timeslot_beg: str = "0h00",
        timeslot_end: str = "23h59",
        freq: str = "30min",
    ) -> pd.DataFrame:
        """Aggregate occupancy by regions

        Parameters
        ----------
        regions : pd.DataFrame
            Mapping between segment, side_of_street and regions.
        days: str, optional
            days to compute, by default 'lun-ven'
        timeslot_beg : str, optional
            starting hour, by default '0h00'
        timeslot_end : str, optional
            ending hour, by default '23h59'
        freq : str, optional
            analysis frequence, by default '30min'

        Returns
        -------
        pd.DataFrame
            _description_
        """
        occ_df = self.to_dataframe()

        return occup.agg_regions(
            occ_df, regions, days, timeslot_beg, timeslot_end, freq
        )

    def occupancy_whole_study(
        self,
        days: str = "lun-dim",
        timeslot_beg: str = "0h00",
        timeslot_end: str = "23h59",
        freq: str = "30min",
    ) -> pd.DataFrame:
        """Aggregate occupancy on the whole study

        Parameters
        ----------
        days: str, optional
            days to compute, by default 'lun-ven'
        timeslot_beg : str, optional
            starting hour, by default '0h00'
        timeslot_end : str, optional
            ending hour, by default '23h59'
        freq : str, optional
            analysis frequence, by default '30min'

        Returns
        -------
        pd.DataFrame
            _description_
        """
        occ_df = self.to_dataframe()

        regions = occ_df.copy()
        regions[constants.SECTEUR_NAME] = "All"
        regions = regions[
            [constants.SEGMENT, constants.SIDE_OF_STREET, constants.SECTEUR_NAME]
        ]
        regions = regions.drop_duplicates()

        occ = occup.agg_regions(occ_df, regions, days, timeslot_beg, timeslot_end, freq)

        occ = occ.drop(columns=constants.SECTEUR_NAME).T
        occ.columns = ["occ"]
        occ.index = occ.index.set_names(names=["hour"])

        return occ

    def occupancy_worst_hour(
        self,
        days: str = "lun-dim",
        timeslot_beg: str = "0h00",
        timeslot_end: str = "23h59",
        worst_hour: int | None = None,
    ) -> pd.DataFrame:
        """Get the highest occupancy hour of the study

        Parameters
        ----------
        days: str, optional
            days to compute, by default 'lun-ven'
        timeslot_beg : str, optional
            starting hour, by default '0h00'
        timeslot_end : str, optional
            ending hour, by default '23h59'
        worst_hour : str, optional
            Worst time to compute. If None, take the hour with the maximum
            occupancy, by default None.

        Returns
        -------
        pd.DataFrame
        """

        if worst_hour is None:
            occ_hr = self.occupancy_whole_study(
                days=days,
                timeslot_beg=timeslot_beg,
                timeslot_end=timeslot_end,
                freq="1h",
            )
            idx = np.argmax(occ_hr)
            worst_hour = occ_hr.iloc[idx].name
            worst_hour = int(worst_hour[:2])

        occ, veh, cap, res = self.occupancy_time_aggregation(
            days=days, timeslot_beg=timeslot_beg, timeslot_end=timeslot_end, freq="1h"
        )
        data = occup.merge_occupancy_capacity_vehicule(occ, cap, veh, res)

        occ_worst_hour = data.xs(worst_hour, level="hour", drop_level=False)
        occ_worst_hour = prepare_data_before_export(
            occ_worst_hour.reset_index(), self.street_geometry
        )
        return occ_worst_hour

    def occupancy_optimal(
        self,
        days: str = "lun-dim",
        timeslot_beg: str = "0h00",
        timeslot_end: str = "23h59",
    ) -> gpd.GeoDataFrame:
        """Get the count of hour where occupancy is above optimal

        Parameters
        ----------
        days: str, optional
            days to compute, by default 'lun-ven'
        timeslot_beg : str, optional
            starting hour, by default '0h00'
        timeslot_end : str, optional
            ending hour, by default '23h59'

        Returns
        -------
        gpd.GeoDataFrame
        """

        occ, veh, cap, res = self.occupancy_time_aggregation(
            days=days, timeslot_beg=timeslot_beg, timeslot_end=timeslot_end, freq="1h"
        )

        return occup.get_optimal_occupancy(occ, cap, veh, res, self.street_geometry)

    def parking_time(
        self,
        days: str = "lun-dim",
        timeslot_beg: str = "0h00",
        timeslot_end: str = "23h59",
    ) -> pd.DataFrame:
        """Compute parking time for each plate in the study

        Parameters
        ----------
        timeslot_beg : str, optional
            starting hour, by default '0h00'
        timeslot_end : str, optional
            ending hour, by default '23h59'

        Returns
        -------
        pd.DataFrame
            Time of each parking instance.
        """
        occ_df = self.to_dataframe()
        occ_df = occ_df.explode(constants.PLATE)
        occ_df[constants.DATETIME] = occ_df[constants.LAP_TIME]
        occ_df[constants.POINT_ON_STREET] = 0
        # remove nan plates
        occ_df = occ_df.dropna(subset=constants.PLATE)

        lap_info = self.get_laps()
        lap_info.columns = [constants.UUID, "first", "last"]
        lap_info = lap_info.sort_index()

        return rempla.compile_parking_time(
            occ_df,
            lap_info,
            days,
            timeslot_beg,
            timeslot_end,
        )

    def reassignement(
        self,
        roads: gpd.GeoDataFrame,
        street_name_to_report: list[str] | str,
        days: str = "lun-dim",
        timeslot_beg: str = "00h00",
        timeslot_end: str = "23h59",
        freq="30min",
        hours: list[str] = None,
    ) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, list[int]]:
        """_summary_

        Parameters
        ----------
        roads : gpd.GeoDataFrame
            _description_
        street_name_to_report : list[str] | str
            _description_
        timeslot_beg : str, optional
            _description_, by default '00h00'
        timeslot_end : str, optional
            _description_, by default '23h59'
        freq : str, optional
            _description_, by default '30min'

        Returns
        -------
        tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, list[int]]
            _description_

        Raises
        ------
        ValueError
            _description_
        """

        roads = roads.to_crs(constants.MONTREAL_CRS)
        roads = roads.reset_index()

        spot_r = SpotReassignement.from_geobase(
            roads,
            street_name_to_report,
            idx_name=constants.SEGMENT,
            col_road_name=constants.ROAD_NAME,
        )

        _, veh, cap, _ = self.occupancy_time_aggregation(
            days, timeslot_beg, timeslot_end, freq
        )
        veh = veh.set_index([constants.SEGMENT, constants.SIDE_OF_STREET])
        cap = cap.set_index([constants.SEGMENT, constants.SIDE_OF_STREET])

        if spot_r == -1:
            raise ValueError(
                "Street name not in roads dataframe", street_name_to_report
            )

        if not hours:
            hours = [
                col
                for col in cap.columns
                if col not in [constants.SEGMENT, constants.SIDE_OF_STREET]
            ]

        report, dist, dist_max, _, _ = spot_r.compute_hr_reassignement(cap, veh, hours)

        return report, dist, dist_max, spot_r.road_ids

    def number_of_vehicules_scanned(
        self,
        days: str = "lun-dim",
        timeslot_beg: str = "00h00",
        timeslot_end: str = "23h59",
    ) -> pd.DataFrame:
        """_summary_

        Parameters
        ----------
        days : str, optional
            _description_, by default 'lun-dim'
        timeslot_beg : str, optional
            _description_, by default '00h00'
        timeslot_end : str, optional
            _description_, by default '23h59'

        Returns
        -------
        pd.DataFrame
            _description_
        """

        occ_df = self.to_dataframe()
        occ_df = occ_df.explode(constants.PLATE)
        occ_df[constants.DATETIME] = occ_df[constants.LAP_TIME]

        return basic.compute_observation_stats(occ_df, days, timeslot_beg, timeslot_end)

    @property
    def street_geometry(self):
        """Return the geometry of the streets.

        Returns
        -------
        pandas.DataFrame | geopandas.GeoDataFrame
        """
        street_geom = []
        perm_regulations = []
        visited = []
        for visited_segment in self.segments:
            if visited_segment.segment.unique_id in visited:
                continue

            street_geom.append(
                pd.DataFrame.from_dict(
                    visited_segment.segment.to_json(), orient="index"
                ).T
            )
            unique_regulations = set(visited_segment.regulations)
            if len(unique_regulations) == 1:
                perm_regulations.append(unique_regulations.pop())
            else:
                perm_regulations.append(None)

            visited.append(visited_segment.segment.unique_id)

        street_geom = pd.concat(street_geom)
        street_geom[constants.CAP_RESTRICTIONS] = perm_regulations
        street_geom = street_geom.drop_duplicates()

        if "geometry" in street_geom.columns:
            street_geom = gpd.GeoDataFrame(
                street_geom, crs=self.segments[0].segment.crs
            )

        not_visited = self._not_visited.copy()
        not_visited[constants.CAP_RESTRICTIONS] = "Non parcourue"

        if (
            isinstance(street_geom, gpd.GeoDataFrame)
            and not_visited.crs != street_geom.crs
        ):
            not_visited = not_visited.to_crs(street_geom.crs)

        street_geom = pd.concat([street_geom, not_visited])
        street_geom = street_geom.drop_duplicates()

        street_geom = street_geom.set_index(["segment", "side_of_street"])

        return street_geom
