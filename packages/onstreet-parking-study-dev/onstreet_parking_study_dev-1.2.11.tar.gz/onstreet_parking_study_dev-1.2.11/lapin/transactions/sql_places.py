
####################################################################################
# Querry to import all places that where present in a given period, active or not. #
####################################################################################

PLACE_SQL_PERIOD = '''        
    SELECT DISTINCT SK_D_Place, No_Place, Ind_SurRue_HorsRue, P.Tarif_Hr, No_Troncon, Rue_Principal, Rue_Xversal_1, Rue_Xversal_2, Cote_Rue, Latitude, Longitude
    FROM D_Place P
    LEFT JOIN D_Troncon T ON P.SK_D_Troncon = T.SK_D_Troncon
    WHERE 1=1 
        AND P.Ind_Actif = 'Actif'
        AND Latitude IS NOT NULL            -- Don't want null point object
        --AND Ind_SurRue_HorsRue = 'Sur rue'
'''
PERIOD_FILTER_SQL_PLACE = '''
        (P.MD_Dt_Expir >= '{beg_date}'
        AND P.MD_Dt_Effectif <= '{end_date}')
'''


##########################################################
# Querry to import all active places during a given day. #
##########################################################

PLACES_ACTIVE_SQL = '''        
    SELECT DISTINCT SK_D_Place, No_Place, Latitude, Longitude
    FROM D_Place P
    WHERE 1=1 
    AND P.Ind_Actif = 'Actif'
    {whr_cond}
'''
DATE_FILTER_SQL_PLACE = '''
    '{date}' between P.MD_Dt_Effectif AND P.MD_Dt_Expir
'''
PLACE_FILTER_SQL_PLACE = '''
    AND SK_D_Place IN {place_filter}
'''
