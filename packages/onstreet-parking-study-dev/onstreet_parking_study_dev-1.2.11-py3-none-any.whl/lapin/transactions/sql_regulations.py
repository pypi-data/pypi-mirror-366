
##########################################################################################################
# Recovers all minutes where parking is allowed during the day (i.e. without active regulation) by hour. #
##########################################################################################################

SQL_REGLEMENT_PREPARE = '''
	drop table if exists ##EchantillonReglement; 
	drop table if exists ##ReglprioriteMin;  
	drop table if exists ##ReglementApplicable; 
    drop table if exists ##ReglTmp;

    declare @wday varchar(50)
    set @WDay = datepart(weekday, '{date}'); --Dimanche = 1, Lundi = 2, Mardi = 3, Mercredi = 4, Jeudi = 5, Vendredi = 6, Samedi = 7

    ----------------------------------------------------------------------------
    -- Création des règlementations actives
    ----------------------------------------------------------------------------
             
    With FilteredRegulation AS(
    SELECT * 
    FROM [dbo].[D_Reglement] I
    WHERE 1=1
    AND    '{date}'  between MD_Dt_Effectif and MD_Dt_Expir 
    AND    '{date}' between cast(cast(year('{date}') as Varchar(4)) +'-'+ right(DT_Deb_Regl, 2)+'-'+ left(DT_Deb_Regl, 2) as date) and cast(cast(year('{date}') as Varchar(4)) +'-'+ right(DT_Fin_Regl, 2)+'-'+ left(DT_Fin_Regl, 2) as date)
    AND Type_Regl NOT IN ('P', 'Q', 'M', 'D', 'V') -- Les types de règles qui sont des durées max
    AND case    when @WDay = 1 then Ind_Dim
                when @WDay = 2 then Ind_Lun
                when @WDay = 3 then Ind_Mar
                when @WDay = 4 then Ind_Mer
                when @WDay = 5 then Ind_Jeu
                when @WDay = 6 then Ind_Ven
                when @WDay = 7 then Ind_Sam
        end = 'Oui'    
    {whr_cond}
    ),
    Permis AS(           -- Tous les permis qui ne sont pas des durée maximum et sont actif pendant la journée en question
    SELECT    SK_D_Regl
    ,        Code_Regl
    ,        No_Place_Terrain
    ,        Type_Regl
    ,        Priorite_Regl
    ,        Ind_Interdiction
    ,        cast(cast('{date}' as Varchar(10)) + ' ' + cast(Hr_Deb_Regl as varchar(8)) as datetime) as DebutReglement
    ,        cast(cast('{date}' as Varchar(10)) + ' ' + cast(Hr_fin_Regl as varchar(8)) as datetime) as FinReglement
    ,         Ind_Lun
    ,        Ind_Mar
    ,        Ind_Mer
    ,        Ind_Jeu
    ,        Ind_Ven
    ,        Ind_Sam
    ,        Ind_Dim
    ,        Tarif_Hr
    ,        Mnt_Quot_Max
    ,        MD_Dt_Effectif
    ,        MD_Dt_Expir 
    FROM    FilteredRegulation
    WHERE 1=1
    AND Ind_Interdiction = 'Permis'
    ),
    Interdictions AS (    -- Toutes les interdictions qui recouvrent au moins une période d'un permis
    SELECT    I.SK_D_Regl
    ,        I.Code_Regl
    ,        I.No_Place_Terrain
    ,        I.Type_Regl
    ,        I.Priorite_Regl
    ,        I.Ind_Interdiction
    -- Les débuts et fin des interdictions sont tronquées à celle du permis
    ,        CASE WHEN cast(cast('{date}' as Varchar(10)) + ' ' + cast(I.Hr_Deb_Regl as varchar(8)) as datetime) < 
                        P.DebutReglement THEN dateadd(mi, datediff(mi, 0, dateadd(s, 30, P.DebutReglement)), 0)
                    ELSE dateadd(mi, datediff(mi, 0, dateadd(s, 30, cast(cast('{date}' as Varchar(10)) + ' ' + cast(I.Hr_Deb_Regl as varchar(8)) as datetime))), 0)
            END as DebutReglement
    ,        CASE WHEN cast(cast('{date}' as Varchar(10)) + ' ' + cast(I.Hr_fin_Regl as varchar(8)) as datetime) >=
                        P.FinReglement THEN  dateadd(mi, datediff(mi, 0, dateadd(s, 30, P.FinReglement)), 0)
                    ELSE dateadd(mi, datediff(mi, 0, dateadd(s, 30, cast(cast('{date}' as Varchar(10)) + ' ' + cast(I.Hr_fin_Regl as varchar(8)) as datetime))), 0)
            END as FinReglement
    ,         I.Ind_Lun
    ,        I.Ind_Mar
    ,        I.Ind_Mer
    ,        I.Ind_Jeu
    ,        I.Ind_Ven
    ,        I.Ind_Sam
    ,        I.Ind_Dim
    ,        I.Tarif_Hr
    ,        I.Mnt_Quot_Max
    ,        I.MD_Dt_Effectif
    ,        I.MD_Dt_Expir 
    FROM    FilteredRegulation  I
    LEFT JOIN Permis P ON P.No_Place_Terrain = I.No_Place_Terrain
    WHERE    I.Ind_Interdiction = 'Interdit'
        AND cast(cast('{date}' as Varchar(10)) + ' ' + cast(I.Hr_Deb_Regl as varchar(8)) as datetime) <
            P.FinReglement 
        AND P.DebutReglement <
            cast(cast('{date}' as Varchar(10)) + ' ' + cast(I.Hr_fin_Regl as varchar(8)) as datetime)
    ),
    Reglements as
    (
        SELECT    *
        from    Permis 
        UNION ALL
        SELECT    *
        from    Interdictions
    )
    select    *
    into    ##EchantillonReglement
    from    Reglements;
 
            
    print 'Reglement Echantillonage terminé :' + cast(getdate() as varchar(30));
    

    WITH MinPrioriteInterdit AS
    (
        SELECT No_Place_Terrain
        ,        MIN(Priorite_Regl) as Priorite_Regl_Min
        FROM    ##EchantillonReglement
        WHERE    Ind_Interdiction = 'Interdit'  
        group by 
                No_Place_Terrain
        
    )
    , MinPrioritePermis AS
    (
        SELECT No_Place_Terrain
        ,        DebutReglement 
        ,        FinReglement 
        ,        MIN(Priorite_Regl) as Priorite_Regl_Min
        FROM    ##EchantillonReglement
        WHERE    Ind_Interdiction = 'Permis'  
        group by 
                No_Place_Terrain
        ,        DebutReglement 
        ,        FinReglement 
        
    )
    , MinPriorite as
    (
        SELECT    No_Place_Terrain
        ,        Priorite_Regl_Min
        from    MinPrioriteInterdit 
        UNION ALL
        SELECT    No_Place_Terrain
        ,        Priorite_Regl_Min
        from    MinPrioritePermis     
    )
    select    *
    into    ##ReglprioriteMin
    from    MinPriorite;

    --reglement terrain
    Select        R.No_Place_Terrain 
    ,            '{date}'                                                                                            as DateRegl
    ,            staging.stg.fn_CalculMesureJsonTrancheHeure(R.DebutReglement, R.FinReglement, '{date}',NULL)        as Nb_Min_Dispo_Regl 
    ,            case when Ind_Interdiction = 'Permis' then R.SK_D_Regl else -2 end                                    as SK_D_Regl_Permis 
    ,            case when Ind_Interdiction = 'Permis' then -2 else R.SK_D_Regl end                                    as SK_D_Regl_Interdit 
    ,            case when Ind_Interdiction = 'Permis' then  Mnt_Quot_Max else 0 end                                    as Mnt_Quot_Max
    ,            Tarif_Hr
    ,            case when Ind_Interdiction = 'Permis' and Mnt_Quot_Max > 0.00 then 'Oui' else 'Non' end                AS Ind_Duree_Max
    ,            R.DebutReglement
    ,            R.FinReglement        
    ,            case when Ind_Interdiction = 'Permis' then 1 else -1 end                                            as FacteurSomme
    ,            cast(0.00 as numeric(8,2)) as Hr00
    ,            cast(0.00 as numeric(8,2)) as Hr01
    ,            cast(0.00 as numeric(8,2)) as Hr02
    ,            cast(0.00 as numeric(8,2)) as Hr03
    ,            cast(0.00 as numeric(8,2)) as Hr04
    ,            cast(0.00 as numeric(8,2)) as Hr05
    ,            cast(0.00 as numeric(8,2)) as Hr06
    ,            cast(0.00 as numeric(8,2)) as Hr07
    ,            cast(0.00 as numeric(8,2)) as Hr08
    ,            cast(0.00 as numeric(8,2)) as Hr09
    ,            cast(0.00 as numeric(8,2)) as Hr10
    ,            cast(0.00 as numeric(8,2)) as Hr11
    ,            cast(0.00 as numeric(8,2)) as Hr12
    ,            cast(0.00 as numeric(8,2)) as Hr13
    ,            cast(0.00 as numeric(8,2)) as Hr14
    ,            cast(0.00 as numeric(8,2)) as Hr15
    ,            cast(0.00 as numeric(8,2)) as Hr16
    ,            cast(0.00 as numeric(8,2)) as Hr17
    ,            cast(0.00 as numeric(8,2)) as Hr18
    ,            cast(0.00 as numeric(8,2)) as Hr19
    ,            cast(0.00 as numeric(8,2)) as Hr20
    ,            cast(0.00 as numeric(8,2)) as Hr21
    ,            cast(0.00 as numeric(8,2)) as Hr22
    ,            cast(0.00 as numeric(8,2)) as Hr23
    ,            'Terrain'                                                                                            as TypeReglement
    into        ##ReglementApplicable
    from        ##EchantillonReglement R
    inner join    ##ReglprioriteMin      P    on P.No_Place_Terrain = R.No_Place_Terrain and P.Priorite_Regl_Min = R.Priorite_Regl 
    where        R.No_Place_Terrain in (select No_place from dbo.D_Place where SK_D_Terrain > 0 and '{date}' between MD_Dt_Effectif AND MD_Dt_Expir);

    --reglement place
    insert into ##ReglementApplicable
    Select        R.No_Place_Terrain 
    ,            '{date}'                                                                                                    as DateRegl
    ,            staging.stg.fn_CalculMesureJsonTrancheHeurePlageVariable(R.DebutReglement, R.FinReglement, '{date}',NULL)    as Nb_Min_Dispo_Regl 
    ,            case when Ind_Interdiction = 'Permis' then R.SK_D_Regl else -2 end                                            as SK_D_Regl_Permis 
    ,            case when Ind_Interdiction = 'Permis' then -2 else R.SK_D_Regl end                                            as SK_D_Regl_Interdit 
    ,            case when Ind_Interdiction = 'Permis' then  Mnt_Quot_Max else 0 end                                            as Mnt_Quot_Max
    ,            Tarif_Hr
    ,            case when Ind_Interdiction = 'Permis' and Mnt_Quot_Max > 0.00 then 'Oui' else 'Non' end                        AS Ind_Duree_Max
    ,            R.DebutReglement
    ,            R.FinReglement        
    ,            case when Ind_Interdiction = 'Permis' then 1 else -1 end                                                    as FacteurSomme
    ,            cast(0.00 as numeric(8,2)) as Hr00
    ,            cast(0.00 as numeric(8,2)) as Hr01
    ,            cast(0.00 as numeric(8,2)) as Hr02
    ,            cast(0.00 as numeric(8,2)) as Hr03
    ,            cast(0.00 as numeric(8,2)) as Hr04
    ,            cast(0.00 as numeric(8,2)) as Hr05
    ,            cast(0.00 as numeric(8,2)) as Hr06
    ,            cast(0.00 as numeric(8,2)) as Hr07
    ,            cast(0.00 as numeric(8,2)) as Hr08
    ,            cast(0.00 as numeric(8,2)) as Hr09
    ,            cast(0.00 as numeric(8,2)) as Hr10
    ,            cast(0.00 as numeric(8,2)) as Hr11
    ,            cast(0.00 as numeric(8,2)) as Hr12
    ,            cast(0.00 as numeric(8,2)) as Hr13
    ,            cast(0.00 as numeric(8,2)) as Hr14
    ,            cast(0.00 as numeric(8,2)) as Hr15
    ,            cast(0.00 as numeric(8,2)) as Hr16
    ,            cast(0.00 as numeric(8,2)) as Hr17
    ,            cast(0.00 as numeric(8,2)) as Hr18
    ,            cast(0.00 as numeric(8,2)) as Hr19
    ,            cast(0.00 as numeric(8,2)) as Hr20
    ,            cast(0.00 as numeric(8,2)) as Hr21
    ,            cast(0.00 as numeric(8,2)) as Hr22
    ,            cast(0.00 as numeric(8,2)) as Hr23
    ,            'Place'                                                                                                        as TypeReglement
    from        ##EchantillonReglement R
    inner join    ##ReglprioriteMin      P    on P.No_Place_Terrain = R.No_Place_Terrain and P.Priorite_Regl_Min = R.Priorite_Regl 
    where        R.No_Place_Terrain not in (select No_place from dbo.D_Place where SK_D_Terrain > 0 and '{date}' between MD_Dt_Effectif AND MD_Dt_Expir);
            
    --on update les colonnes avec les bonnes informations: plus rapide en 2 updates.
    update ##ReglementApplicable    set    Hr00    = cast(json_value(Nb_Min_Dispo_Regl, '$.Hr00') as numeric(8,2))
    ,                                    Hr01    = cast(json_value(Nb_Min_Dispo_Regl, '$.Hr01') as numeric(8,2))
    ,                                    Hr02    = cast(json_value(Nb_Min_Dispo_Regl, '$.Hr02') as numeric(8,2))
    ,                                    Hr03    = cast(json_value(Nb_Min_Dispo_Regl, '$.Hr03') as numeric(8,2))
    ,                                    Hr04    = cast(json_value(Nb_Min_Dispo_Regl, '$.Hr04') as numeric(8,2))
    ,                                    Hr05    = cast(json_value(Nb_Min_Dispo_Regl, '$.Hr05') as numeric(8,2))
    ,                                    Hr06    = cast(json_value(Nb_Min_Dispo_Regl, '$.Hr06') as numeric(8,2))
    ,                                    Hr07    = cast(json_value(Nb_Min_Dispo_Regl, '$.Hr07') as numeric(8,2))
    ,                                    Hr08    = cast(json_value(Nb_Min_Dispo_Regl, '$.Hr08') as numeric(8,2))
    ,                                    Hr09    = cast(json_value(Nb_Min_Dispo_Regl, '$.Hr09') as numeric(8,2))
    ,                                    Hr10    = cast(json_value(Nb_Min_Dispo_Regl, '$.Hr10') as numeric(8,2))
    ,                                    Hr11    = cast(json_value(Nb_Min_Dispo_Regl, '$.Hr11') as numeric(8,2))
    ,                                    Hr12    = cast(json_value(Nb_Min_Dispo_Regl, '$.Hr12') as numeric(8,2))
    ,                                    Hr13    = cast(json_value(Nb_Min_Dispo_Regl, '$.Hr13') as numeric(8,2))
    ,                                    Hr14    = cast(json_value(Nb_Min_Dispo_Regl, '$.Hr14') as numeric(8,2))
    ,                                    Hr15    = cast(json_value(Nb_Min_Dispo_Regl, '$.Hr15') as numeric(8,2))
    ,                                    Hr16    = cast(json_value(Nb_Min_Dispo_Regl, '$.Hr16') as numeric(8,2))
    ,                                    Hr17    = cast(json_value(Nb_Min_Dispo_Regl, '$.Hr17') as numeric(8,2))
    ,                                    Hr18    = cast(json_value(Nb_Min_Dispo_Regl, '$.Hr18') as numeric(8,2))
    ,                                    Hr19    = cast(json_value(Nb_Min_Dispo_Regl, '$.Hr19') as numeric(8,2))
    ,                                    Hr20    = cast(json_value(Nb_Min_Dispo_Regl, '$.Hr20') as numeric(8,2))
    ,                                    Hr21    = cast(json_value(Nb_Min_Dispo_Regl, '$.Hr21') as numeric(8,2))
    ,                                    Hr22    = cast(json_value(Nb_Min_Dispo_Regl, '$.Hr22') as numeric(8,2))
    ,                                    Hr23    = cast(json_value(Nb_Min_Dispo_Regl, '$.Hr23') as numeric(8,2));
        
    update ##ReglementApplicable
    set      Hr00     = FacteurSomme*Hr00
    ,        Hr01     = FacteurSomme*Hr01
    ,        Hr02     = FacteurSomme*Hr02
    ,        Hr03     = FacteurSomme*Hr03
    ,        Hr04     = FacteurSomme*Hr04
    ,        Hr05     = FacteurSomme*Hr05
    ,        Hr06     = FacteurSomme*Hr06
    ,        Hr07     = FacteurSomme*Hr07
    ,        Hr08     = FacteurSomme*Hr08
    ,        Hr09     = FacteurSomme*Hr09
    ,        Hr10     = FacteurSomme*Hr10
    ,        Hr11     = FacteurSomme*Hr11
    ,        Hr12     = FacteurSomme*Hr12
    ,        Hr13     = FacteurSomme*Hr13
    ,        Hr14     = FacteurSomme*Hr14
    ,        Hr15     = FacteurSomme*Hr15
    ,        Hr16     = FacteurSomme*Hr16
    ,        Hr17     = FacteurSomme*Hr17
    ,        Hr18     = FacteurSomme*Hr18
    ,        Hr19     = FacteurSomme*Hr19
    ,        Hr20     = FacteurSomme*Hr20
    ,        Hr21     = FacteurSomme*Hr21
    ,        Hr22     = FacteurSomme*Hr22
    ,        Hr23     = FacteurSomme*Hr23
                
    select    No_Place_Terrain
                ,        DateRegl

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
                
                into    ##ReglTmp
                from    ##ReglementApplicable --ToutesReglesMin    
                where    TypeReglement = 'Place'
                group by    No_Place_Terrain
                ,            DateRegl
                ,            TypeReglement ;

                insert into ##ReglTmp
                select    No_Place_Terrain
                ,        DateRegl
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

                from    ##ReglementApplicable --ToutesReglesMin    
                where    TypeReglement = 'Terrain'
                group by    No_Place_Terrain
                ,            DateRegl
                ,            TypeReglement ;
'''

SQL_REGLEMENT = '''
    select 
        No_Place_Terrain as No_Place,
        Hr00,
        Hr01,
        Hr02,
        Hr03,
        Hr04,
        Hr05,
        Hr06,
        Hr07,
        Hr08,
        Hr09,
        Hr10,
        Hr11,
        Hr12,
        Hr13,
        Hr14,
        Hr15,
        Hr16,
        Hr17,
        Hr18,
        Hr19,
        Hr20,
        Hr21,
        Hr22,
        Hr23
    from ##ReglTmp;
'''

SQL_REGLEMENT_CLOSE = '''
	drop table if exists ##EchantillonReglement; 
	drop table if exists ##ReglprioriteMin;  
	drop table if exists ##ReglementApplicable; 
    drop table if exists ##ReglTmp;
'''

PLACE_SQL_REG = '''
AND I.No_Place_Terrain in {place_filter}
'''
