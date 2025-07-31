"""Trajectory DataFrame

Originated from scikit-mobility repo :
https://github.com/scikit-mobility/scikit-mobility/blob/master/skmob/core/trajectorydataframe.py
"""

from warnings import warn

from typing import Callable
import geopandas as gpd
import numpy as np
import pandas as pd

from lapin import constants
from lapin.io.azure_cosmos import cosmos_db_to_geodataframe
from lapin.tools.utils import parse_tz_mixed_time_offsets
from lapin.io.sql import query_engine, get_engine
from lapin.io.types import EngineConfig


class TrajSeries(pd.Series):
    @property
    def _constructor(self):
        return TrajSeries

    @property
    def _constructor_expanddim(self):
        return TrajDataFrame


class TrajDataFrame(pd.DataFrame):
    """TrajDataFrame.

    A TrajDataFrame object is a pandas.DataFrame that has three columns
    latitude, longitude and datetime. TrajDataFrame accepts the following
    keyword arguments:

    Parameters
    ----------
    data : list or dict or pandas DataFrame
        the data that must be embedded into a TrajDataFrame.

    latitude : int or str, optional
        the position or the name of the column in `data` containing the
        latitude.  The default is `constants.LATITUDE`.

    longitude : int or str, optional
        the position or the name of the column in `data` containing the
        longitude.  The default is `constants.LONGITUDE`.

    datetime : int or str, optional
        the position or the name of the column in `data` containing the
        datetime.  The default is `constants.DATETIME`.

    user_id : int or str, optional
        the position or the name of the column in `data`containing the user
        identifier.  The default is `constants.UID`.

    timestamp : boolean, optional
        it True, the datetime is a timestamp.
        The default is `False`.

    crs : dict, optional
        the coordinate reference system of the geographic points.
        The default is `{"init": "epsg:4326"}`.

    parameters : dict, optional
        parameters to add to the TrajDataFrame. The default is `{}`
        (no parameters).

    Examples
    --------
    >>> import lapin
    >>> # create a TrajDataFrame from a list
    >>> data_list = [[1, 39.984094, 116.319236, '2008-10-23 13:53:05'],
     [1, 39.984198, 116.319322, '2008-10-23 13:53:06'],
     [1, 39.984224, 116.319402, '2008-10-23 13:53:11'],
     [1, 39.984211, 116.319389, '2008-10-23 13:53:16']]
    >>> tdf = lapin.TrajDataFrame(data_list, latitude=1,
                                  longitude=2, datetime=3)
    >>> print(tdf.head())
       0        lat         lng            datetime
    0  1  39.984094  116.319236 2008-10-23 13:53:05
    1  1  39.984198  116.319322 2008-10-23 13:53:06
    2  1  39.984224  116.319402 2008-10-23 13:53:11
    3  1  39.984211  116.319389 2008-10-23 13:53:16
    >>> print(type(tdf))
    <class 'skmob.core.trajectorydataframe.TrajDataFrame'>
    >>>
    >>> # create a TrajDataFrame from a pandas DataFrame
    >>> import pandas as pd
    >>> # create a DataFrame from the previous list
    >>> data_df = pd.DataFrame(data_list, columns=['user', 'latitude',
                                                   'lng', 'hour'])
    >>> print(type(data_df))
    <class 'pandas.core.frame.DataFrame'>
    >>> tdf = skmob.TrajDataFrame(data_df, latitude='latitude',
                                  datetime='hour', user_id='user')
    >>> print(type(tdf))
    <class 'skmob.core.trajectorydataframe.TrajDataFrame'>
    >>> print(tdf.head())
       uid        lat         lng            datetime
    0    1  39.984094  116.319236 2008-10-23 13:53:05
    1    1  39.984198  116.319322 2008-10-23 13:53:06
    2    1  39.984224  116.319402 2008-10-23 13:53:11
    3    1  39.984211  116.319389 2008-10-23 13:53:16
    """

    # All the metadata that should be accessible must be also in the metadata
    # method
    _metadata = [
        "_parameters",
        "_crs",
    ]

    def __init__(
        self,
        data,
        latitude=constants.LATITUDE,
        longitude=constants.LONGITUDE,
        datetime=constants.DATETIME,
        user_id=constants.UUID,
        timestamp=False,
        crs="epsg:4326",
        parameters={},
        date_kwargs=None,
        **kwargs,
    ):

        original2default = {
            latitude: constants.LATITUDE,
            longitude: constants.LONGITUDE,
            datetime: constants.DATETIME,
            user_id: constants.UUID,
        }

        columns = None

        if isinstance(data, pd.DataFrame):
            tdf = data.rename(columns=original2default)
            columns = tdf.columns

        # Dictionary
        elif isinstance(data, dict):
            tdf = pd.DataFrame.from_dict(data).rename(columns=original2default)
            columns = tdf.columns

        # List
        elif isinstance(data, list) or isinstance(data, np.ndarray):
            tdf = data
            columns = []
            num_columns = len(data[0])
            for i in range(num_columns):
                try:
                    columns += [original2default[i]]
                except KeyError:
                    columns += [i]

        elif isinstance(data, pd.core.internals.BlockManager):
            tdf = data

        else:
            raise TypeError(
                "DataFrame constructor called with incompatible "
                + f"data and dtype: {type(data)}"
            )

        if "columns" in kwargs:
            super().__init__(tdf, **kwargs)
        else:
            super().__init__(tdf, columns=columns, **kwargs)

        # Check crs consistency
        if crs is None:
            warn("crs will be set to the default crs WGS84 (EPSG:4326).")

        if not isinstance(crs, str):
            raise TypeError("crs must be a dict type.")

        self._crs = crs

        if not isinstance(parameters, dict):
            raise AttributeError("parameters must be a dictionary.")

        self._parameters = parameters

        if not date_kwargs:
            date_kwargs = parameters.get("date_kwargs", {})
        self._parameters["date_kwargs"] = date_kwargs

        if self._has_traj_columns():
            self._set_traj(timestamp=timestamp, inplace=True)

    def _has_traj_columns(self):

        if (
            (constants.DATETIME in self)
            and (constants.LATITUDE in self)
            and (constants.LONGITUDE in self)
        ):
            return True

        return False

    def _is_trajdataframe(self):
        if (
            (
                constants.DATETIME in self
                and pd.core.dtypes.common.is_datetime64_any_dtype(
                    self[constants.DATETIME]
                )
            )
            and (
                constants.LONGITUDE in self
                and pd.core.dtypes.common.is_float_dtype(self[constants.LONGITUDE])
            )
            and (
                constants.LATITUDE in self
                and pd.core.dtypes.common.is_float_dtype(self[constants.LATITUDE])
            )
        ):
            return True

        return False

    def _set_traj(self, timestamp=False, inplace=False):

        if not inplace:
            frame = self.copy()
        else:
            frame = self

        if timestamp:
            frame[constants.DATETIME] = parse_tz_mixed_time_offsets(
                frame[constants.DATETIME], unit="s"
            )

        if not pd.core.dtypes.common.is_datetime64_any_dtype(
            frame[constants.DATETIME].dtype
        ):
            frame[constants.DATETIME] = parse_tz_mixed_time_offsets(
                frame[constants.DATETIME], **self._parameters["date_kwargs"]
            )
        if "tz" in self._parameters["date_kwargs"]:
            frame[constants.DATETIME] = frame[constants.DATETIME].dt.tz_convert(
                self._parameters["date_kwargs"]["tz"]
            )

        if not pd.core.dtypes.common.is_float_dtype(frame[constants.LONGITUDE].dtype):
            frame[constants.LONGITUDE] = frame[constants.LONGITUDE].astype("float")

        if not pd.core.dtypes.common.is_float_dtype(frame[constants.LATITUDE].dtype):
            frame[constants.LATITUDE] = frame[constants.LATITUDE].astype("float")

        frame.parameters = self._parameters
        frame.crs = self._crs

        if not inplace:
            return frame
        else:
            return None

    def to_geodataframe(self) -> gpd.GeoDataFrame:
        """To geodataframe

        Returns
        -------
        geopandas.GeoDataFrame
        """
        gdf = gpd.GeoDataFrame(
            self.copy(),
            geometry=gpd.points_from_xy(
                self[constants.LONGITUDE], self[constants.LATITUDE]
            ),
            crs=self._crs,
        )

        return gdf

    def __getitem__(self, key):
        """
        If the result contains lat, lng and datetime, return a TrajDataFrame,
        else a pandas DataFrame.
        """
        result = super().__getitem__(key)

        if (isinstance(result, TrajDataFrame)) and result._is_trajdataframe():
            result.__class__ = TrajDataFrame
            result.crs = self._crs
            result.parameters = self._parameters

        elif isinstance(result, TrajDataFrame) and not result._is_trajdataframe():
            result.__class__ = pd.DataFrame

        return result

    def settings_from(self, frame):
        """
        Copy the attributes from another TrajDataFrame.

        Parameters
        ----------
        trajdataframe : TrajDataFrame
            the TrajDataFrame from which to copy the attributes.

        Examples
        --------
        >>> import skmob
        >>> import pandas as pd
        >>> # read the trajectory data (GeoLife, Beijing, China)
        >>> url = skmob.utils.constants.GEOLIFE_SAMPLE
        >>> df = pd.read_csv(url, sep=',', compression='gzip')
        >>> tdf1 = skmob.TrajDataFrame(df, latitude='lat', longitude='lon',
                                       user_id='user', datetime='datetime')
        >>> tdf1 = skmob.TrajDataFrame(df, latitude='lat', longitude='lon',
                                       user_id='user', datetime='datetime')
        >>> print(tdf1.parameters)
        {}
        >>> tdf2.parameters['hasProperty'] = True
        >>> print(tdf2.parameters)
        {'hasProperty': True}
        >>> tdf1.settings_from(tdf2)
        >>> print(tdf1.parameters)
        {'hasProperty': True}
        """
        for k in frame.metadata:
            value = getattr(frame, k)
            setattr(self, k, value)

    @classmethod
    def from_postgres(
        cls,
        engine_conf: EngineConfig,
        schema: str,
        table: str,
        dates: list[dict[str, str]],
        date_col: str,
        tdf_columns_config: dict | None = None,
    ):

        engine = get_engine(**engine_conf)
        query_sql = f"""
            select
             t.*
            from {schema}.{table} t
            """

        df = query_engine(
            engine=engine, query=query_sql, dates=dates, date_col=date_col
        )

        if "geom" in df.columns:
            df = df.drop(columns="geom")

        # change timezone
        dt_columns = df.select_dtypes(include=["datetime64[ns, UTC]"]).columns
        for dt_col in dt_columns:
            df[dt_col] = df[dt_col].dt.tz_convert(constants.PROJECT_TIMEZONE)

        if tdf_columns_config:
            return cls(df, **tdf_columns_config)
        else:
            return cls(df)

    @classmethod
    def from_azure_cosmos(
        cls,
        query: str,
        dates: list[dict[str, str]],
        date_col: str,
        cosmos_config: dict,
        enable_cross_partition_query: bool = True,
        tdf_columns_config: dict | None = None,
        func: Callable | None = None,
    ):
        """Load data from azure cosmos

        Parameters
        ----------
        query: str,
            Querry to launch.
        dates: list[dict[str, str]]
            Dates querried with fromat {'from': date, 'to':date}>
        date_col: str
            Date column in azure cosmos.
        cosmos_config: dict
            Cosmos db configurations.
        enable_cross_partition_query: bool, optional
            Query accross multiple partion, by default True.
        tdf_columns_config: dict
            Columns configurations.
        func: func, optional
            post_processing function to apply to data, by default None.

        Returns
        -------
        TrajDataFrame
        """
        gdf = cosmos_db_to_geodataframe(
            query=query,
            cosmos_config=cosmos_config,
            dates=dates,
            date_col=date_col,
            enable_cross_partition_query=enable_cross_partition_query,
        )

        if func:
            gdf = func(gdf, tdf_columns_config)

        return cls(gdf, **tdf_columns_config)

    @classmethod
    def from_file(
        cls,
        filename,
        latitude=constants.LATITUDE,
        longitude=constants.LONGITUDE,
        datetime=constants.DATETIME,
        user_id=constants.UUID,
        encoding=None,
        usecols=None,
        header="infer",
        timestamp=False,
        crs="epsg:4326",
        sep=",",
        parameters=None,
    ):
        """
        Read a trajectory file and return a TrajDataFrame.

        Parameters
        ----------
        filename : str
            the path to the file
        latitude : str, optional
            the name of the column containing the latitude values
        longitude : str, optional
            the name of the column containing the longitude values
        datetime : str, optional
            the name of the column containing the datetime values
        user_id : str, optional
            the name of the column containing the user id values
        trajectory_id : str, optional
            the name of the column containing the trajectory id values
        encoding : str, optional
            the encoding of the file
        usecols : list, optional
            the columns to read
        header : int, optional
            the row number of the header
        timestamp : bool, optional
            if True, the datetime column contains timestamps
        crs : dict, optional
            the coordinate reference system of the TrajDataFrame
        sep : str, optional
            the separator of the file
        parameters : dict, optional
            the parameters of the TrajDataFrame

        Returns
        -------
        TrajDataFrame
            The loaded TrajDataFrame

        """
        df = pd.read_csv(
            filename, sep=sep, header=header, usecols=usecols, encoding=encoding
        )

        if parameters is None:
            # Init prop dictionary
            parameters = {"from_file": filename}

        return cls(
            df,
            latitude=latitude,
            longitude=longitude,
            datetime=datetime,
            user_id=user_id,
            parameters=parameters,
            crs=crs,
            timestamp=timestamp,
        )

    @property
    def lat(self):
        """_summary_

        Returns
        -------
        _type_
            _description_

        Raises
        ------
        AttributeError
            _description_
        """
        if constants.LATITUDE not in self:
            raise AttributeError(
                "The TrajDataFrame does not contain the"
                + f" column {constants.LATITUDE}."
            )
        return self[constants.LATITUDE]

    @property
    def lng(self):
        """_summary_

        Returns
        -------
        _type_
            _description_

        Raises
        ------
        AttributeError
            _description_
        """
        if constants.LONGITUDE not in self:
            raise AttributeError(
                "The TrajDataFrame does not contain the"
                + f" column {constants.LONGITUDE}."
            )
        return self[constants.LONGITUDE]

    @property
    def datetime(self):
        """_summary_

        Returns
        -------
        _type_
            _description_

        Raises
        ------
        AttributeError
            _description_
        """
        if constants.DATETIME not in self:
            raise AttributeError(
                "The TrajDataFrame does not contain the"
                + f" column {constants.DATETIME}."
            )
        return self[constants.DATETIME]

    @property
    def _constructor(self):
        return TrajDataFrame

    @property
    def _constructor_sliced(self):
        return TrajSeries

    @property
    def _constructor_expanddim(self):
        return TrajDataFrame

    @property
    def metadata(self):
        # Add here all the metadata that are accessible from the object
        md = ["crs", "parameters"]
        return md

    def __finalize__(self, other, method=None, **kwargs):
        """propagate metadata from other to self"""
        # merge operation: using metadata of the left object
        if method == "merge":
            for name in self._metadata:
                object.__setattr__(self, name, getattr(other.left, name, None))

        # concat operation: using metadata of the first object
        elif method == "concat":
            for name in self._metadata:
                object.__setattr__(self, name, getattr(other.objs[0], name, None))
        else:
            for name in self._metadata:
                object.__setattr__(self, name, getattr(other, name, None))

        return self

    def set_parameter(self, key, param):
        """_summary_

        Parameters
        ----------
        key : _type_
            _description_
        param : _type_
            _description_
        """
        self._parameters[key] = param

    @property
    def crs(self):
        """_summary_

        Returns
        -------
        _type_
            _description_
        """
        return self._crs

    @crs.setter
    def crs(self, crs):
        self._crs = crs

    @property
    def parameters(self):
        """_summary_

        Returns
        -------
        _type_
            _description_
        """
        return self._parameters

    @parameters.setter
    def parameters(self, parameters):

        self._parameters = dict(parameters)

    def sort_by_uid_and_datetime(self):
        """_summary_

        Returns
        -------
        _type_
            _description_
        """
        if constants.UUID in self.columns:
            return self.sort_values(
                by=[constants.UUID, constants.DATETIME], ascending=[True, True]
            )
        else:
            return self.sort_values(by=[constants.DATETIME], ascending=[True])

    def timezone_conversion(self, from_timezone, to_timezone):
        """
        Convert the timezone of the datetime in the TrajDataFrame.

        Parameters
        ----------
        from_timezone : str
            the current timezone of the TrajDataFrame (e.g., 'GMT').

        to_timezone : str
            the new timezone of the TrajDataFrame (e.g., 'Asia/Shanghai').

        Examples
        --------
        >>> import skmob
        >>> import pandas as pd
        >>> # read the trajectory data (GeoLife, Beijing, China)
        >>> url = skmob.utils.constants.GEOLIFE_SAMPLE
        >>> df = pd.read_csv(url, sep=',', compression='gzip')
        >>> tdf = skmob.TrajDataFrame(df, latitude='lat', longitude='lon',
                                      user_id='user', datetime='datetime')
        >>> print(tdf.head())
                 lat         lng            datetime  uid
        0  39.984094  116.319236 2008-10-23 05:53:05    1
        1  39.984198  116.319322 2008-10-23 05:53:06    1
        2  39.984224  116.319402 2008-10-23 05:53:11    1
        3  39.984211  116.319389 2008-10-23 05:53:16    1
        4  39.984217  116.319422 2008-10-23 05:53:21    1
        >>> tdf.timezone_conversion('GMT', 'Asia/Shanghai')
        >>> print(tdf.head())
                 lat         lng  uid            datetime
        0  39.984094  116.319236    1 2008-10-23 13:53:05
        1  39.984198  116.319322    1 2008-10-23 13:53:06
        2  39.984224  116.319402    1 2008-10-23 13:53:11
        3  39.984211  116.319389    1 2008-10-23 13:53:16
        4  39.984217  116.319422    1 2008-10-23 13:53:21
        """
        self.rename(columns={"datetime": "original_datetime"}, inplace=True)
        self["datetime"] = (
            self["original_datetime"]
            .dt.tz_localize(from_timezone)
            .dt.tz_convert(to_timezone)
            .dt.tz_localize(None)
        )
        self.drop(columns=["original_datetime"], inplace=True)


def nparray_to_trajdataframe(trajectory_array, columns, parameters={}):
    """_summary_

    Parameters
    ----------
    trajectory_array : _type_
        _description_
    columns : _type_
        _description_
    parameters : dict, optional
        _description_, by default {}

    Returns
    -------
    _type_
        _description_
    """
    df = pd.DataFrame(trajectory_array, columns=columns)
    tdf = TrajDataFrame(df, parameters=parameters)
    return tdf


def _dataframe_set_geometry(
    self, col, timestampe=False, drop=False, inplace=False, crs=None
):
    if inplace:
        raise ValueError(
            "Can't do inplace setting when converting from"
            + " DataFrame to GeoDataFrame"
        )
    gf = TrajDataFrame(self)

    # this will copy so that BlockManager gets copied
    return gf._set_traj()


pd.DataFrame._set_traj = _dataframe_set_geometry
