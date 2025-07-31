''' Utils for the models

Module provide function slice_data_by_hour
'''
import pandas as pd
from lapin.tools.ctime import Ctime
from lapin.tools.utils import parse_days


def slice_data_by_hour(
    data: pd.DataFrame,
    days: str,
    from_hour: str,
    to_hour: str,
    time_col: str = 'time'
) -> pd.DataFrame:
    """ Return DataFrame with only the record that are in the specified
    time window.

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe to slice.
    from_hour : str
        Starting hour for slicing, by default '0h00'. In a format that
        lapin.tools.ctime.Ctime.from_string can read.
    to_hour : str
        Stoping hour for slicing occupancy, by default '23h59'. In a format
        that lapin.tools.ctime.Ctime.from_string can read.
    time_col : str, optional
        Columns containing datetime, by default 'time'

    Returns
    -------
    pd.DataFrame
        Filtered DataFrame
    """
    data = data.copy()

    # datetime to ctime
    data['ctime'] = [Ctime.from_datetime(t) for t in data[time_col]]

    # parse relevant hours
    timeslot_beg = Ctime.from_string(from_hour)
    timeslot_end = Ctime.from_string(to_hour)

    # parse day
    days_l = parse_days(days)

    data = data[
        (data[time_col].dt.day_of_week.isin(days_l)) &
        (data['ctime'] >= timeslot_beg) &
        (data['ctime'] <= timeslot_end)
    ]
    data.drop(columns='ctime', inplace=True)

    return data


def dist_list_to_dataframe(d_list: list, colnames: list) -> pd.DataFrame:
    """For reassignement. Handle the distance output.

    Parameters
    ----------
    d_list : list
        Distance list
    colnames : list
        Names of the columns

    Returns
    -------
    pd.DataFrame
        Output
    """
    res = []

    for i, col in enumerate(colnames):

        dist_df = pd.DataFrame(d_list[i]).T.reset_index().rename(
            columns={'index': 'segment'}
        )
        dist_df['hour'] = col
        dist_df = dist_df.set_index(['segment', 'hour'])

        res.append(dist_df)

    dist_df = pd.concat(res)

    return dist_df