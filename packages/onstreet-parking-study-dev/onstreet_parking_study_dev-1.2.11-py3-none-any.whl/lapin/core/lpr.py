''' Module that provide the LPR DataFrame structure '''
import pandas as pd
import numpy as np

from lapin.core.trajectory import TrajDataFrame, TrajSeries
from lapin.constants import lpr_data as constants


class LprSeries(TrajSeries):
    @property
    def _constructor(self):
        return LprSeries

    @property
    def _constructor_expanddim(self):
        return LprDataFrame


class LprDataFrame(TrajDataFrame):
    """TrajDataFrame.

    A LprDataFrame object is a pandas.DataFrame that has four columns: plate,
    latitude, longitude and datetime. LprDataFrame accepts the following
    keyword arguments:

    Parameters
    ----------
    data : list or dict or pandas DataFrame
        the data that must be embedded into a TrajDataFrame.

    plate : int or str, optional
        the position or the name of the column in `data` containing the plates.
        The defautl is `constants.PLATE`

    latitude : int or str, optional
        the position or the name of the column in `data` containing the
        latitude. The default is `constants.LATITUDE`.

    longitude : int or str, optional
        the position or the name of the column in `data` containing the
        longitude.  The default is `constants.LONGITUDE`.

    datetime : int or str, optional
        the position or the name of the column in `data` containing the
        datetime.  The default is `constants.DATETIME`.

    user_id : int or str, optional
        the position or the name of the column in `data`containing the user
        identifier.  The default is `constants.UID`.

    side_of_car: int or str, optional
        the position or the name of the column in `data`containing the side of
        the camera.  The default is `constants.UID`.

    timestamp : boolean, optional
        it True, the datetime is a timestamp.
        The default is `False`.

    crs : dict, optional
        the coordinate reference system of the geographic points.
        The default is `{"init": "epsg:4326"}`.

    parameters : dict, optional
        parameters to add to the TrajDataFrame. The default is `{}` (no
        parameters).

    Examples
    --------
    >>> import lapin
    >>> # create a TrajDataFrame from a list
    >>> data_list = [[1, 39.984094, 116.319236, '2008-10-23 13:53:05'],
     [1, 39.984198, 116.319322, '2008-10-23 13:53:06'],
     [1, 39.984224, 116.319402, '2008-10-23 13:53:11'],
     [1, 39.984211, 116.319389, '2008-10-23 13:53:16']]
    >>> tdf = lapin.TrajDataFrame(data_list, latitude=1, longitude=2,
                                  datetime=3)
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

    # All the metadata that should be accessible must be also in the
    # metadata method
    _metadata = [
        "_parameters",
        "_crs",
    ]

    def __init__(
        self,
        data,
        plate: str = constants.PLATE,
        latitude: str = constants.LATITUDE,
        longitude: str = constants.LONGITUDE,
        datetime: str = constants.DATETIME,
        user_id: str = constants.UUID,
        side_of_car: str = constants.SIDE_OF_CAR,
        data_index: str = None,
        timestamp: bool = False,
        crs: str = "epsg:4326",
        parameters: dict = {},
        date_kwargs: dict = None,
    ):

        original2default = {
            plate: constants.PLATE,
            latitude: constants.LATITUDE,
            longitude: constants.LONGITUDE,
            datetime: constants.DATETIME,
            user_id: constants.UUID,
            side_of_car: constants.SIDE_OF_CAR,
        }

        if isinstance(data, pd.DataFrame):
            lpr = data.rename(columns=original2default)

        # Dictionary
        elif isinstance(data, dict):
            lpr = pd.DataFrame.from_dict(data).rename(columns=original2default)
            columns = lpr.columns

        # List
        elif isinstance(data, list) or isinstance(data, np.ndarray):
            lpr = data
            columns = []
            num_columns = len(data[0])
            for i in range(num_columns):
                try:
                    columns += [original2default[i]]
                except KeyError:
                    columns += [i]
            lpr = pd.DataFrame(data=lpr, columns=columns)

        super().__init__(
            lpr,
            latitude,
            longitude,
            datetime,
            user_id,
            timestamp,
            crs,
            parameters,
            date_kwargs
        )

        if data_index is None and constants.INDEX not in self.columns:
            self.reset_index(names=constants.INDEX, inplace=True)
        else:
            self.rename(columns={data_index: constants.INDEX}, inplace=True)

        if self._has_lpr_columns():
            self._set_lpr(timestamp=timestamp, inplace=True)

    def _has_lpr_columns(self):
        if self._has_traj_columns() and (constants.PLATE in self):
            return True

        return False

    def _is_lprdataframe(self):
        if (
            self._is_trajdataframe() and
            ((constants.PLATE in self) and
             pd.api.types.is_string_dtype(self[constants.PLATE]))
        ):

            return True

        return False

    def _set_lpr(self, timestamp=False, inplace=False):
        frame = self._set_traj(timestamp, inplace)

        return frame

    def __getitem__(self, key):
        """
        If the result contains lat, lng and datetime, return a TrajDataFrame,
        else a pandas DataFrame.
        """
        result = super().__getitem__(key)

        if (
            isinstance(result, LprDataFrame) and
            result._is_lprdataframe()
        ):
            result.__class__ = LprDataFrame
            result.crs = self._crs
            result.parameters = self._parameters

        elif (
            isinstance(result, TrajDataFrame)
        ):
            try:
                result = LprDataFrame(result)
                result.__class__ = LprDataFrame
                result.crs = self._crs
                result.parameters = self._parameters
            except ValueError:
                result.__class__ = TrajDataFrame

        elif (
            isinstance(result, TrajDataFrame) and
            result._is_trajdataframe()
        ):
            result.__class__ = TrajDataFrame

        elif (
            isinstance(result, LprDataFrame) and
            not result._is_lprdataframe()
        ):
            result.__class__ = pd.DataFrame

        return result

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
        crs={"init": "epsg:4326"},
        sep=",",
        parameters=None,
        date_kwargs=None,
        plate=constants.PLATE,
        side_of_car=constants.SIDE_OF_CAR,
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
        date_kwargs : dict, optional
            the parameters of the tiemstamp

        Returns
        -------
        TrajDataFrame
            The loaded TrajDataFrame

        """
        df = pd.read_csv(
            filename,
            sep=sep,
            header=header,
            usecols=usecols,
            encoding=encoding
        )

        if parameters is None:
            # Init prop dictionary
            parameters = {"from_file": filename}

        return cls(
            df,
            plate=plate,
            latitude=latitude,
            longitude=longitude,
            datetime=datetime,
            user_id=user_id,
            side_of_car=side_of_car,
            parameters=parameters,
            crs=crs,
            timestamp=timestamp,
            date_kwargs=date_kwargs,
        )

    @property
    def plate(self):
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
        if constants.PLATE not in self:
            raise AttributeError(
                "The TrajDataFrame does not contain the column" +
                f"{constants.PLATE}."
            )
        return self[constants.PLATE]

    @property
    def side_of_car(self):
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
        if constants.SIDE_OF_CAR not in self:
            raise AttributeError(
                "The TrajDataFrame does not contain the column" +
                f"{constants.SIDE_OF_CAR}."
            )
        return self[constants.SIDE_OF_CAR]

    @property
    def _constructor(self):
        return LprDataFrame

    @property
    def _constructor_sliced(self):
        return LprSeries

    @property
    def _constructor_expanddim(self):
        return LprDataFrame


def nparray_to_trajdataframe(
    trajectory_array,
    columns,
    parameters={}
):
    df = pd.DataFrame(trajectory_array, columns=columns)
    tdf = LprDataFrame(df, parameters=parameters)
    return tdf


def _dataframe_set_geometry(
    self,
    inplace=False,
):
    if inplace:
        raise ValueError(
            "Can't do inplace setting when converting from" +
            " DataFrame to GeoDataFrame"
        )
    gf = LprDataFrame(self)

    # this will copy so that BlockManager gets copied
    return gf._set_lpr()


pd.DataFrame._set_lpr = _dataframe_set_geometry
