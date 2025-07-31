
###################################################################
# Retrieve all effective permits duration during a day (by hour). #
###################################################################

SQL_ODP = """
    SET NOCOUNT ON;
    drop table if exists ##ODPTmp; 
    drop table if exists ##ODPAgg; 

    -- Get active permits during a day.
    with PermisODP as (
        SELECT    
                 No_Place_ODP,
                 max(No_permis)    as DernierDebute
                 
        FROM     [dbo].[D_PermisODP] P
        
        WHERE    1=1
        {whr_cond}
        
        GROUP BY No_Place_ODP
        )


    -- Transform start/end duration into hour bucket columns.

    SELECT    P.No_Place_ODP    
    ,        '{date}'                                                                                                            as Dt_Des_Permis
    ,        staging.stg.fn_CalculMesureJsonTrancheHeurePlageVariable(P.DH_Deb_Permis, P.DH_Fin_Permis, '{date}',NULL)            as Nb_Min_ODP
    ,        cast(0.00 as numeric(8,2))                                                                                            as Hr00
    ,        cast(0.00 as numeric(8,2))                                                                                            as Hr01
    ,        cast(0.00 as numeric(8,2))                                                                                            as Hr02
    ,        cast(0.00 as numeric(8,2))                                                                                            as Hr03
    ,        cast(0.00 as numeric(8,2))                                                                                            as Hr04
    ,        cast(0.00 as numeric(8,2))                                                                                            as Hr05
    ,        cast(0.00 as numeric(8,2))                                                                                            as Hr06
    ,        cast(0.00 as numeric(8,2))                                                                                            as Hr07
    ,        cast(0.00 as numeric(8,2))                                                                                            as Hr08
    ,        cast(0.00 as numeric(8,2))                                                                                            as Hr09
    ,        cast(0.00 as numeric(8,2))                                                                                            as Hr10
    ,        cast(0.00 as numeric(8,2))                                                                                            as Hr11
    ,        cast(0.00 as numeric(8,2))                                                                                            as Hr12
    ,        cast(0.00 as numeric(8,2))                                                                                            as Hr13
    ,        cast(0.00 as numeric(8,2))                                                                                            as Hr14
    ,        cast(0.00 as numeric(8,2))                                                                                            as Hr15
    ,        cast(0.00 as numeric(8,2))                                                                                            as Hr16
    ,        cast(0.00 as numeric(8,2))                                                                                            as Hr17
    ,        cast(0.00 as numeric(8,2))                                                                                            as Hr18
    ,        cast(0.00 as numeric(8,2))                                                                                            as Hr19
    ,        cast(0.00 as numeric(8,2))                                                                                            as Hr20
    ,        cast(0.00 as numeric(8,2))                                                                                            as Hr21
    ,        cast(0.00 as numeric(8,2))                                                                                            as Hr22
    ,        cast(0.00 as numeric(8,2))                                                                                            as Hr23
    into        ##ODPTmp
    FROM        [dbo].[D_PermisODP]  P
    inner join    PermisODP             F on P.No_Place_ODP = F.No_Place_ODP and P.No_permis = F.DernierDebute     
    WHERE          1=1
    {whr_cond}

    --on update les colonnes avec les bonnes informations: plus rapide en 2 updates.
    update ##ODPTmp    set    Hr00 = cast(json_value(Nb_Min_ODP, '$.Hr00') as numeric(8,2));
    update ##ODPTmp    set    Hr01 = cast(json_value(Nb_Min_ODP, '$.Hr01') as numeric(8,2));
    update ##ODPTmp    set    Hr02 = cast(json_value(Nb_Min_ODP, '$.Hr02') as numeric(8,2));
    update ##ODPTmp    set    Hr03 = cast(json_value(Nb_Min_ODP, '$.Hr03') as numeric(8,2));
    update ##ODPTmp    set    Hr04 = cast(json_value(Nb_Min_ODP, '$.Hr04') as numeric(8,2));
    update ##ODPTmp    set    Hr05 = cast(json_value(Nb_Min_ODP, '$.Hr05') as numeric(8,2));
    update ##ODPTmp    set    Hr06 = cast(json_value(Nb_Min_ODP, '$.Hr06') as numeric(8,2));
    update ##ODPTmp    set    Hr07 = cast(json_value(Nb_Min_ODP, '$.Hr07') as numeric(8,2));
    update ##ODPTmp    set    Hr08 = cast(json_value(Nb_Min_ODP, '$.Hr08') as numeric(8,2));
    update ##ODPTmp    set    Hr09 = cast(json_value(Nb_Min_ODP, '$.Hr09') as numeric(8,2));
    update ##ODPTmp    set    Hr10 = cast(json_value(Nb_Min_ODP, '$.Hr10') as numeric(8,2));
    update ##ODPTmp    set    Hr11 = cast(json_value(Nb_Min_ODP, '$.Hr11') as numeric(8,2));
    update ##ODPTmp    set    Hr12 = cast(json_value(Nb_Min_ODP, '$.Hr12') as numeric(8,2));
    update ##ODPTmp    set    Hr13 = cast(json_value(Nb_Min_ODP, '$.Hr13') as numeric(8,2));
    update ##ODPTmp    set    Hr14 = cast(json_value(Nb_Min_ODP, '$.Hr14') as numeric(8,2));
    update ##ODPTmp    set    Hr15 = cast(json_value(Nb_Min_ODP, '$.Hr15') as numeric(8,2));
    update ##ODPTmp    set    Hr16 = cast(json_value(Nb_Min_ODP, '$.Hr16') as numeric(8,2));
    update ##ODPTmp    set    Hr17 = cast(json_value(Nb_Min_ODP, '$.Hr17') as numeric(8,2));
    update ##ODPTmp    set    Hr18 = cast(json_value(Nb_Min_ODP, '$.Hr18') as numeric(8,2));
    update ##ODPTmp    set    Hr19 = cast(json_value(Nb_Min_ODP, '$.Hr19') as numeric(8,2));
    update ##ODPTmp    set    Hr20 = cast(json_value(Nb_Min_ODP, '$.Hr20') as numeric(8,2));
    update ##ODPTmp    set    Hr21 = cast(json_value(Nb_Min_ODP, '$.Hr21') as numeric(8,2));
    update ##ODPTmp    set    Hr22 = cast(json_value(Nb_Min_ODP, '$.Hr22') as numeric(8,2));
    update ##ODPTmp    set    Hr23 = cast(json_value(Nb_Min_ODP, '$.Hr23') as numeric(8,2));

    SET NOCOUNT OFF;
    select    No_Place_ODP as No_Place
    ,        case when sum(Hr00)>60 then 60.00 else case when sum(Hr00)<0 then 0.00 else sum(Hr00) end end    as Hr00
    ,        case when sum(Hr01)>60 then 60.00 else case when sum(Hr01)<0 then 0.00 else sum(Hr01) end end    as Hr01
    ,        case when sum(Hr02)>60 then 60.00 else case when sum(Hr02)<0 then 0.00 else sum(Hr02) end end    as Hr02
    ,        case when sum(Hr03)>60 then 60.00 else case when sum(Hr03)<0 then 0.00 else sum(Hr03) end end    as Hr03
    ,        case when sum(Hr04)>60 then 60.00 else case when sum(Hr04)<0 then 0.00 else sum(Hr04) end end    as Hr04
    ,        case when sum(Hr05)>60 then 60.00 else case when sum(Hr05)<0 then 0.00 else sum(Hr05) end end    as Hr05
    ,        case when sum(Hr06)>60 then 60.00 else case when sum(Hr06)<0 then 0.00 else sum(Hr06) end end    as Hr06
    ,        case when sum(Hr07)>60 then 60.00 else case when sum(Hr07)<0 then 0.00 else sum(Hr07) end end    as Hr07
    ,        case when sum(Hr08)>60 then 60.00 else case when sum(Hr08)<0 then 0.00 else sum(Hr08) end end    as Hr08
    ,        case when sum(Hr09)>60 then 60.00 else case when sum(Hr09)<0 then 0.00 else sum(Hr09) end end    as Hr09
    ,        case when sum(Hr10)>60 then 60.00 else case when sum(Hr10)<0 then 0.00 else sum(Hr10) end end    as Hr10
    ,        case when sum(Hr11)>60 then 60.00 else case when sum(Hr11)<0 then 0.00 else sum(Hr11) end end    as Hr11
    ,        case when sum(Hr12)>60 then 60.00 else case when sum(Hr12)<0 then 0.00 else sum(Hr12) end end    as Hr12
    ,        case when sum(Hr13)>60 then 60.00 else case when sum(Hr13)<0 then 0.00 else sum(Hr13) end end    as Hr13
    ,        case when sum(Hr14)>60 then 60.00 else case when sum(Hr14)<0 then 0.00 else sum(Hr14) end end    as Hr14
    ,        case when sum(Hr15)>60 then 60.00 else case when sum(Hr15)<0 then 0.00 else sum(Hr15) end end    as Hr15
    ,        case when sum(Hr16)>60 then 60.00 else case when sum(Hr16)<0 then 0.00 else sum(Hr16) end end    as Hr16
    ,        case when sum(Hr17)>60 then 60.00 else case when sum(Hr17)<0 then 0.00 else sum(Hr17) end end    as Hr17
    ,        case when sum(Hr18)>60 then 60.00 else case when sum(Hr18)<0 then 0.00 else sum(Hr18) end end    as Hr18
    ,        case when sum(Hr19)>60 then 60.00 else case when sum(Hr19)<0 then 0.00 else sum(Hr19) end end    as Hr19
    ,        case when sum(Hr20)>60 then 60.00 else case when sum(Hr20)<0 then 0.00 else sum(Hr20) end end    as Hr20
    ,        case when sum(Hr21)>60 then 60.00 else case when sum(Hr21)<0 then 0.00 else sum(Hr21) end end    as Hr21
    ,        case when sum(Hr22)>60 then 60.00 else case when sum(Hr22)<0 then 0.00 else sum(Hr22) end end    as Hr22
    ,        case when sum(Hr23)>60 then 60.00 else case when sum(Hr23)<0 then 0.00 else sum(Hr23) end end    as Hr23
    from    ##ODPTmp
    group by No_Place_ODP
"""

PLACE_COND_ODP = """
    AND            P.Statut_Permis   IN ('Actif')            
    AND            P.Type_Permis_ODP in ( 'Capuchonner', 'Enlever') 
    AND            P.SK_D_Permis_ODP > 0
    AND            P.No_Place_ODP IN {place_filter}
"""

DATE_COND_ODP = """
     '{date}' BETWEEN cast(P.DH_Deb_Permis as date) AND cast(P.DH_Fin_Permis as date)
"""
