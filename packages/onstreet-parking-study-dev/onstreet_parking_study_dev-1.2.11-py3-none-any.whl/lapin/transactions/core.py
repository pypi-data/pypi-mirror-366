import sys
import time
import datetime
import logging
import numpy as np
import pandas as pd
import geopandas as gpd
import pymssql

from .connections import AXES, PARK_OCCUPANCY, STAGING
from .querry import PLACE_SQL, PARK_OCCUPANCY_SQL, DATE_FILTER_SQL_PLACE, DATE_FILTER_TRANSAC, PARK_TRANSACTIONNB_SQL, PLACE_FILTER_TRANSAC, SQL_PLACES_ODP, DATE_FILTER_ODP, PLACE_FILTER_ODP
from . import sql_places
from . import sql_permits
from . import sql_regulations
from . import sql_transactions
from . import utils
from . import constants
from ..tools.geom import rtreenearest
from ..tools.utils import deprecated
from ..tools.utils import parse_days
from ..tools.ctime import Ctime

logger = logging.getLogger(__name__)


#####################
###### PLACES #######
#####################

def extract_parking_slot(periods, zone=gpd.GeoDataFrame()):
    """ TODO
    """

    # retrieve place between date range
    con = pymssql.connect(**AXES)
    sql = sql_places.PLACE_SQL_PERIOD
    whr_cond = 'AND '
    for period in periods:
        whr_cond += sql_places.PERIOD_FILTER_SQL_PLACE.format(beg_date=period['from'], end_date=period['to'])
        whr_cond += 'OR '
    whr_cond += '1=2'
    sql += whr_cond
    data = pd.read_sql(con=con, sql=sql)
    data["No_Place"] = data["No_Place"].str.strip()

    # filter by zone
    data_gdf = gpd.GeoDataFrame(
        data,
        geometry=gpd.points_from_xy(data[constants.LNG], data[constants.LAT]),
        crs='epsg:4326'
    )
    if not zone.empty:
        data_gdf = gpd.sjoin(data_gdf, zone.to_crs('epsg:4326'), op='within')

    return data_gdf

def extract_permit_on_parking_slot(periods=None, list_sk_d_place=None):
    """ TODO DOC
    """
    con = pymssql.connect(**STAGING)
    sql = SQL_PLACES_ODP
    whr_cond = ""

    if periods:
        whr_cond = 'AND ('
        for period in periods:
            whr_cond += DATE_FILTER_ODP.format(beg_date=period['from'], end_date=period['to'])
            whr_cond += ' OR '
        whr_cond += '1=2)'

    if list_sk_d_place:
        whr_cond += PLACE_FILTER_ODP.format(tuple(list_sk_d_place))

    sql += whr_cond

    data = pd.read_sql(con=con, sql=sql)
    data["No_Place"] = data["No_Place"].str.strip()

    return data

def road_match_parking_slot(park_slots, roads):
    """TODO
    """
    park_slots = park_slots.copy()
    roads = roads.copy()

    merged = rtreenearest(
        park_slots.reset_index(drop=True).to_crs('epsg:32188'),
        roads.reset_index(drop=True).to_crs('epsg:32188'),
        gdfB_cols=[constants.SEG_DB_ID, constants.SEG_DB_SIDE, constants.SEG_DB_STREET]
    )

    # TODO : Perform test on distance and street_name
    return merged


###########################
###### TRANSACTIONS #######
###########################

def extract_transactions(periods, sk_d_place, post_filter_noplace=[]):
    """ TODO
    """
    res = []

    for period in periods:
        start_date = pd.to_datetime(period['from'])
        end_date = pd.to_datetime(period['to'])
        delta = datetime.timedelta(days=1)
        end_of_day = datetime.timedelta(hours=23, minutes=59, seconds=59)

        logger.info("Treating period %s", period)
        ## Transactions
        start = time.time()
        transactions = utils.get_data(PARK_OCCUPANCY, sql_transactions.TRANSACTION_SQL,
                                      '', sql_transactions.DATE_FILTER_TRANSAC, '', period)
        end = time.time()
        logger.info("trans %s", end - start)

        while start_date <= end_date:
            sys.stdout.write(f"\r {start_date}")
            sys.stdout.flush()

            ## Places
            start = time.time()
            places_day = utils.get_data(AXES, sql_places.PLACES_ACTIVE_SQL,
                                        sql_places.PLACE_FILTER_SQL_PLACE,
                                        sql_places.DATE_FILTER_SQL_PLACE,
                                        sk_d_place, {'date':start_date})
            end = time.time()
            #print(f"Place : {end - start}")
            places_day_list = tuple(places_day.No_Place.to_list()) if sk_d_place else None
            #places_day_list = tuple(places_day.No_Place.str.strip().to_list()) # Strip because we believe there's non cleanned data
            places_day = places_day.set_index('No_Place')

            ## Transactions
            #start = time.time()
            #data = utils.get_data(PARK_OCCUPANCY, sql_transactions.TRANSACTION_SQL,
            #                      sql_transactions.PLACE_FILTER_TRANSAC,
            #                      sql_transactions.DATE_FILTER_TRANSAC,
            #                      places_day_list, start_date)
            #end = time.time()
            #print(f"Trans : {end - start}")
            data = transactions[
                (transactions.DH_Debut_Prise_Place.dt.date <= start_date.date()) &\
                (transactions.DH_Fin_Prise_Place.dt.date >= start_date.date())
            ].copy().reset_index()
            data['debutReel'] = data['DH_Debut_Prise_Place'].apply(lambda x: max(x, start_date))
            data['finReel'] = data['DH_Fin_Prise_Place'].apply(lambda x: min(x, start_date+end_of_day))

            # hour discretisation
            data = utils.from_transaction_to_hour_bin(data, column_deb='debutReel', column_fin='finReel')
            data = data.set_index('No_Place')

            ## ODP
            start = time.time()
            odp = utils.get_data(AXES, sql_permits.SQL_ODP, sql_permits.PLACE_COND_ODP,
                                 sql_permits.DATE_COND_ODP, places_day_list, {'date':start_date})
            odp = odp.set_index('No_Place')
            end = time.time()
            #print(f"ODP : {end - start}")

            ## Reglementation
            start = time.time()
            # create temp table
            con = utils.getEngine(**AXES)
            utils.get_data(
                con=con,
                sql=sql_regulations.SQL_REGLEMENT_PREPARE,
                place_sql=sql_regulations.PLACE_SQL_REG,
                place_filter=places_day_list,
                date_filter={'date':start_date},
                execute_only=True
            )
            # get regls
            reg = utils.get_data(
                con=con,
                sql=sql_regulations.SQL_REGLEMENT
            )
            # suppress temp tables
            utils.get_data(
                con=AXES,
                sql=sql_regulations.SQL_REGLEMENT_CLOSE,
                execute_only=True
            )
            con.dispose()

            reg = reg.set_index('No_Place')
            end = time.time()
            #print(f"Reg : {end - start}")

            # Join data altogether
            data = places_day.drop(columns='SK_D_Place').join(data, how='left', on='No_Place')
            data = data.join(reg, rsuffix='_regl', how='left', on='No_Place')
            data = data.join(odp, rsuffix='_odp', how='left', on='No_Place')

            data['date'] = start_date

            if post_filter_noplace:
                data = data.loc[np.intersect1d(data.index, post_filter_noplace)]

            # append transactions with regulations
            res.append(data)

            start_date += delta

    return pd.concat(res).reset_index()

def compute_payement_rate(data, periods=None, sk_d_place=None, extract_transac=False):
    """ Compute park payement rate.
    """

    if extract_transac:
        if not (periods or sk_d_place):
            logger.warning('arguments `period` and `sk_d_place` are empty.')
        # get and filter data
        data = extract_transactions(periods, sk_d_place)
    else:
        data = data.copy()

    # Sum all the transaction on the same place/day.
    payement_rates = data[constants.TRS_HOURS_COLS + ['No_Place', 'date']].copy()\
                         .reset_index(drop=True)\
                         .groupby(['No_Place', 'date'])\
                         .sum()\
                         .clip(0,60)

    # Get ODP
    odp_cols = list(data.columns.intersection(constants.ODP_HOURS_COLS)) + ['No_Place', 'date']
    odp = data[odp_cols].copy().reset_index(drop=True).groupby(['No_Place', 'date']).first()
    ## Rename columns
    odp = odp.rename(columns=dict(zip(constants.ODP_HOURS_COLS, constants.TRS_HOURS_COLS)))

    # Get regulations
    reg_cols = list(data.columns.intersection(constants.REG_HOURS_COLS)) + ['No_Place', 'date']
    reg = data[reg_cols].copy().reset_index(drop=True).groupby(['No_Place', 'date']).first()
    ## Rename columns
    reg = reg.rename(columns=dict(zip(constants.REG_HOURS_COLS, constants.TRS_HOURS_COLS)))

    # Filter hours with no right to park
    cols = reg.dropna(axis=1, how='all').columns
    payement_rates = payement_rates[cols]
    reg = reg[cols]
    odp = odp[cols]

    # Compute average payement rates by place/hour
    payement_rates /= (reg.fillna(0) - odp.fillna(0)).clip(0, 60).replace(0, np.nan)

    return payement_rates, reg, odp

def produce_payement_analysis(data, times, places):
    """ Take payement rate for all daysBound and produce payement analysis for day of week
    and hours specified.
    """

    data = data.copy()
    occ_list = []
    for name, days_hours in times.items():
        days = parse_days(days_hours[0])
        start = Ctime.from_string(days_hours[1])
        end = Ctime.from_string(days_hours[2])

        cols = [f'Hr{x:02d}' for x in range(start.hour, end.hour+1)]


        occ_tmp = data.reset_index().copy()

        # Get days of week
        occ_tmp.date = pd.to_datetime(occ_tmp.date)
        occ_tmp['day_of_week'] = occ_tmp.date.dt.day_of_week

        # filter by days of interest
        occ_tmp = occ_tmp[occ_tmp.day_of_week.isin(days)][['No_Place', 'day_of_week'] + cols]
        occ_tmp["day_of_week"] = name


        occ_tmp = ( occ_tmp.melt(['No_Place', 'day_of_week'])
                           .groupby(['No_Place', 'day_of_week'])
                           .agg('mean')
                           .rename(columns={'value':'Occupation Moyenne'})
                           .reset_index() )

        occ_list.append(occ_tmp)

    occ = pd.concat(occ_list)
    occ = occ.pivot(index="No_Place", columns="day_of_week", values='Occupation Moyenne')

    # assert that only one occurance of the place is going on
    places = places.loc[places.sort_values('SK_D_Place')['No_Place'].drop_duplicates(keep='last').index]
    # Add Lat, Lng value
    occ = pd.merge(occ, places[['No_Place', 'Latitude', 'Longitude']], on='No_Place')

    return occ


@deprecated
def extract_park_occupancy(periods, sk_d_place=None, odp_restrictions_as_nan=True):
    """ Deprecated. Should use compute_occupency.

    Retrieve park occupancy from CPTR_Station.
    """

    # retrieve place between date range
    con = pymssql.connect(**PARK_OCCUPANCY)
    sql = PARK_OCCUPANCY_SQL
    whr_cond = PLACE_FILTER_TRANSAC.format(place_filter=sk_d_place) if sk_d_place else ""
    if periods:
        whr_cond += ' AND ('
        for period in periods:
            whr_cond += DATE_FILTER_TRANSAC.format(beg_date=period['from'], end_date=period['to'])
            whr_cond += 'OR '
        whr_cond += '1=2)'
    sql += whr_cond
    data = pd.read_sql(con=con, sql=sql)
    data["No_Place"] = data["No_Place"].str.strip()

    if odp_restrictions_as_nan:
        data = data.replace(-2, np.nan)
    else:
        data = data.replace(0, np.nan)

    return data

def extract_park_transaction_nb(periods, sk_d_place=None):
    """ TODO
    """

    # retrieve place between date range
    con = pymssql.connect(**PARK_OCCUPANCY)
    sql = PARK_TRANSACTIONNB_SQL.format(place_filter=sk_d_place)
    whr_cond = PLACE_FILTER_TRANSAC.format(place_filter=sk_d_place) if sk_d_place else ""
    if periods:
        whr_cond = 'AND ('
        for period in periods:
            whr_cond += DATE_FILTER_TRANSAC.format(beg_date=period['from'], end_date=period['to'])
            whr_cond += 'OR '
        whr_cond += '1=2)'
    sql += whr_cond
    data = pd.read_sql(con=con, sql=sql)
    data["No_Place"] = data["No_Place"].str.strip()

    return data

def road_match_park_occupancy(trans, places_matched):
    """TODO
    """
    trans = trans.copy()
    places_matched = places_matched.copy()

    trans = trans.merge(places_matched[['SK_D_Place', constants.SEG_DB_ID, constants.SEG_DB_SIDE]], on='SK_D_Place')
    trans.rename(columns={
        constants.SEG_DB_ID: constants.SEGMENT,
        constants.SEG_DB_SIDE: constants.SIDE_OF_STREET,
        'Date': constants.DATETIME,
    }, inplace=True)
    trans[constants.SIDE_OF_STREET] = trans[constants.SIDE_OF_STREET].map({'Gauche': -1, 'Droite':1})
    trans.drop(columns=['SK_D_Place', 'No_Place'], inplace=True)

    return trans

class TransactionHandler(object):
    """description of class
    TODO : 2. Permit to filter by dayofweek
    """

    def __init__(self, daysbounds, zone, roads):
        """ TODO : 1. DO the replacement
        """
        places = extract_parking_slot(daysbounds, zone)
        places = road_match_parking_slot(places, roads)

        occ = extract_park_occupancy(daysbounds, tuple(places.SK_D_Place.to_list()))
        occ = road_match_park_occupancy(occ, places)

        nb = extract_park_transaction_nb(daysbounds, tuple(places.SK_D_Place.to_list()))
        nb = road_match_park_occupancy(nb, places)

        self.occupancy = occ
        self.nb_transac = nb

    def _filtering_occ(self, filter='all'):
        """TODO
        """
        data = self.occupancy.copy()

        if filter == 'all':
            return data

        data[constants.DATETIME] = pd.to_datetime(data[constants.DATETIME])
        if filter == 'week_day':
            return data[data[constants.DATETIME].dt.dayofweek.isin([0,1,2,3,4])]
        elif filter == 'week_end':
            return data[data[constants.DATETIME].dt.dayofweek.isin([5,6])]
        else:
            return data


    def occupancy_hour(self, filter):
        """TODO
        """
        data = self._filtering_occ(filter)
        cols = [col for col in data.columns if col not in [constants.DATETIME, constants.SIDE_OF_STREET, constants.SEGMENT]]
        data = data.pivot_table(index=[constants.SEGMENT, constants.SIDE_OF_STREET], values=cols).reset_index()

        return data

    def occupancy_timeslot(self, filter):
        """TODO
        """
        data = self._filtering_occ(filter)
        cols = [col for col in data.columns if col not in [constants.DATETIME, constants.SIDE_OF_STREET, constants.SEGMENT]]
        data = data.groupby([constants.SEGMENT, constants.SIDE_OF_STREET])[cols].agg('mean')\
                                                                .agg('mean', axis=1)\
                                                                .to_frame('mean_occ')\
                                                                .reset_index()

        return data

    def occupancy_days(self, filter):
        """TODO
        """
        data = self._filtering_occ(filter)
        data[constants.DATETIME] = pd.to_datetime(data[constants.DATETIME])
        cols = [col for col in data.columns if col not in [constants.DATETIME, constants.SEG_DB_SIDE, constants.SEG_DB_ID]]
        data.groupby([constants.SEGMENT, constants.SIDE_OF_STREET, data[constants.DATETIME].dt.dayofweek])[cols].agg('mean')\
                                                                                     .agg('mean', axis=1)\
                                                                                     .to_frame('mean_occ')\
                                                                                     .reset_index()
        return data
