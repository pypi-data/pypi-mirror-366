PLACE_SQL = '''        
    SELECT DISTINCT SK_D_Place, No_Place, Ind_SurRue_HorsRue, P.Tarif_Hr, No_Troncon, Rue_Principal, Rue_Xversal_1, Rue_Xversal_2, Cote_Rue, Latitude, Longitude
    FROM D_Place P
    LEFT JOIN D_Troncon T
        ON P.SK_D_Troncon = T.SK_D_Troncon
    WHERE 1=1 
        --AND P.Ind_Actif = 'Actif'
        --AND Ind_SurRue_HorsRue = 'Sur rue'
        AND Latitude IS NOT NULL            -- Don't want null point object
'''
DATE_FILTER_SQL_PLACE = '''
        (P.MD_Dt_Expir >= '{beg_date}'
        AND P.MD_Dt_Effectif <= '{end_date}')
'''

PARK_OCCUPANCY_SQL = '''
SELECT SK_D_Place 
      ,[No_Place_Terrain] No_Place
      ,D.[Date] Date

  -- Taux d'occupation de 09:00
, CASE WHEN (cast(JSON_VALUE(Nb_Min_Dispo_Regl, '$.Hr09') as float) - cast(JSON_VALUE(Nb_Min_ODP, '$.Hr09') as float)) = 0
	   THEN -2
	   ELSE cast(JSON_VALUE(Nb_Min_Paye, '$.Hr09') as float) / (cast(JSON_VALUE(Nb_Min_Dispo_Regl, '$.Hr09') as float) - cast(JSON_VALUE(Nb_Min_ODP, '$.Hr09') as float)) 
  END '09:00'
  
  -- Taux d'occupation de 10:00
, CASE WHEN (cast(JSON_VALUE(Nb_Min_Dispo_Regl, '$.Hr10') as float) - cast(JSON_VALUE(Nb_Min_ODP, '$.Hr10') as float)) = 0
	   THEN -2
	   ELSE cast(JSON_VALUE(Nb_Min_Paye, '$.Hr10') as float) / (cast(JSON_VALUE(Nb_Min_Dispo_Regl, '$.Hr10') as float) - cast(JSON_VALUE(Nb_Min_ODP, '$.Hr10') as float))
  END '10:00'

  -- Taux d'occupation de 11:00
, CASE WHEN (cast(JSON_VALUE(Nb_Min_Dispo_Regl, '$.Hr11') as float) - cast(JSON_VALUE(Nb_Min_ODP, '$.Hr11') as float)) = 0 
	   THEN -2
	   ELSE cast(JSON_VALUE(Nb_Min_Paye, '$.Hr11') as float) / (cast(JSON_VALUE(Nb_Min_Dispo_Regl, '$.Hr11') as float) - cast(JSON_VALUE(Nb_Min_ODP, '$.Hr11') as float))
  END '11:00'

  -- Taux d'occupation de 13:00
, CASE WHEN (cast(JSON_VALUE(Nb_Min_Dispo_Regl, '$.Hr13') as float) - cast(JSON_VALUE(Nb_Min_ODP, '$.Hr13') as float)) = 0
	   THEN -2
       ELSE cast(JSON_VALUE(Nb_Min_Paye, '$.Hr13') as float) / (cast(JSON_VALUE(Nb_Min_Dispo_Regl, '$.Hr13') as float) - cast(JSON_VALUE(Nb_Min_ODP, '$.Hr13') as float))
  END '13:00'

  -- Taux d'occupation de 12:00
, CASE WHEN (cast(JSON_VALUE(Nb_Min_Dispo_Regl, '$.Hr12') as float) - cast(JSON_VALUE(Nb_Min_ODP, '$.Hr12') as float)) = 0
	   THEN -2
       ELSE cast(JSON_VALUE(Nb_Min_Paye, '$.Hr12') as float) / (cast(JSON_VALUE(Nb_Min_Dispo_Regl, '$.Hr12') as float) - cast(JSON_VALUE(Nb_Min_ODP, '$.Hr12') as float))
  END '12:00'

  -- Taux d'occupation de 14:00
, CASE WHEN (cast(JSON_VALUE(Nb_Min_Dispo_Regl, '$.Hr14') as float) - cast(JSON_VALUE(Nb_Min_ODP, '$.Hr14') as float)) = 0
	   THEN -2
       ELSE cast(JSON_VALUE(Nb_Min_Paye, '$.Hr14') as float) / (cast(JSON_VALUE(Nb_Min_Dispo_Regl, '$.Hr14') as float) - cast(JSON_VALUE(Nb_Min_ODP, '$.Hr14') as float))
  END '14:00'

  -- Taux d'occupation de 15:00
, CASE WHEN (cast(JSON_VALUE(Nb_Min_Dispo_Regl, '$.Hr15') as float) - cast(JSON_VALUE(Nb_Min_ODP, '$.Hr15') as float)) = 0
	   THEN -2
       ELSE cast(JSON_VALUE(Nb_Min_Paye, '$.Hr15') as float) / (cast(JSON_VALUE(Nb_Min_Dispo_Regl, '$.Hr15') as float) - cast(JSON_VALUE(Nb_Min_ODP, '$.Hr15') as float))
  END '15:00'

  -- Taux d'occupation de 16:00
, CASE WHEN (cast(JSON_VALUE(Nb_Min_Dispo_Regl, '$.Hr16') as float) - cast(JSON_VALUE(Nb_Min_ODP, '$.Hr16') as float)) = 0
	   THEN -2
       ELSE cast(JSON_VALUE(Nb_Min_Paye, '$.Hr16') as float) / (cast(JSON_VALUE(Nb_Min_Dispo_Regl, '$.Hr16') as float) - cast(JSON_VALUE(Nb_Min_ODP, '$.Hr16') as float))
  END '16:00'

  -- Taux d'occupation de 17:00
, CASE WHEN (cast(JSON_VALUE(Nb_Min_Dispo_Regl, '$.Hr17') as float) - cast(JSON_VALUE(Nb_Min_ODP, '$.Hr17') as float)) = 0
	   THEN -2
       ELSE cast(JSON_VALUE(Nb_Min_Paye, '$.Hr17') as float) / (cast(JSON_VALUE(Nb_Min_Dispo_Regl, '$.Hr17') as float) - cast(JSON_VALUE(Nb_Min_ODP, '$.Hr17') as float))
  END '17:00'

  -- Taux d'occupation de 18:00
, CASE WHEN (cast(JSON_VALUE(Nb_Min_Dispo_Regl, '$.Hr18') as float) - cast(JSON_VALUE(Nb_Min_ODP, '$.Hr18') as float)) = 0
	   THEN -2
       ELSE cast(JSON_VALUE(Nb_Min_Paye, '$.Hr18') as float) / (cast(JSON_VALUE(Nb_Min_Dispo_Regl, '$.Hr18') as float) - cast(JSON_VALUE(Nb_Min_ODP, '$.Hr18') as float))
  END '18:00'

  -- Taux d'occupation de 19:00
, CASE WHEN (cast(JSON_VALUE(Nb_Min_Dispo_Regl, '$.Hr19') as float) - cast(JSON_VALUE(Nb_Min_ODP, '$.Hr19') as float)) = 0
	   THEN -2
       ELSE cast(JSON_VALUE(Nb_Min_Paye, '$.Hr19') as float) / (cast(JSON_VALUE(Nb_Min_Dispo_Regl, '$.Hr19') as float) - cast(JSON_VALUE(Nb_Min_ODP, '$.Hr19') as float))
  END '19:00'

  -- Taux d'occupation de 20:00
, CASE WHEN (cast(JSON_VALUE(Nb_Min_Dispo_Regl, '$.Hr20') as float) - cast(JSON_VALUE(Nb_Min_ODP, '$.Hr20') as float)) = 0
	   THEN -2
       ELSE cast(JSON_VALUE(Nb_Min_Paye, '$.Hr20') as float) / (cast(JSON_VALUE(Nb_Min_Dispo_Regl, '$.Hr20') as float) - cast(JSON_VALUE(Nb_Min_ODP, '$.Hr20') as float))
  END '20:00'

FROM [CPTR_Station].[dbo].[F_ActivitePlaceDetailQuotidien] F
INNER JOIN [Axes].[dbo].[D_Date] D ON D.SK_D_Date = F.SK_D_Date

WHERE 1=1
'''

PARK_TRANSACTIONNB_SQL = """
SELECT SK_D_Place
      ,[No_Place_Terrain] No_Place
      ,D.[Date] Date

-- nb transaction 09:00
, 1 + cast(JSON_VALUE(Nb_Trans_Concur, '$.Hr09') as float) AS '09:00'
 -- nb transaction 10:00
, 1 + cast(JSON_VALUE(Nb_Trans_Concur, '$.Hr10') as float) AS '10:00'
-- nb transaction 11:00
, 1 + cast(JSON_VALUE(Nb_Trans_Concur, '$.Hr11') as float) AS '11:00'
-- nb transaction 12:00
, 1 + cast(JSON_VALUE(Nb_Trans_Concur, '$.Hr12') as float) AS '12:00'
-- nb transaction 13:00
, 1 + cast(JSON_VALUE(Nb_Trans_Concur, '$.Hr13') as float) AS '13:00'
-- nb transaction 14:00
, 1 + cast(JSON_VALUE(Nb_Trans_Concur, '$.Hr14') as float) AS '14:00'
-- nb transaction 15:00
, 1 + cast(JSON_VALUE(Nb_Trans_Concur, '$.Hr15') as float) AS '15:00'
-- nb transaction 16:00
, 1 + cast(JSON_VALUE(Nb_Trans_Concur, '$.Hr16') as float) AS '16:00'
-- nb transaction 17:00
, 1 + cast(JSON_VALUE(Nb_Trans_Concur, '$.Hr17') as float) AS '17:00'
-- nb transaction 18:00
, 1 + cast(JSON_VALUE(Nb_Trans_Concur, '$.Hr18') as float) AS '18:00'
-- nb transaction 19:00
, 1 + cast(JSON_VALUE(Nb_Trans_Concur, '$.Hr19') as float) AS '19:00'
-- nb transaction 20:00
, 1 + cast(JSON_VALUE(Nb_Trans_Concur, '$.Hr20') as float) AS '20:00'


FROM [CPTR_Station].[dbo].[F_ActivitePlaceDetailQuotidien] F
INNER JOIN [Axes].[dbo].[D_Date] D ON D.SK_D_Date = F.SK_D_Date

WHERE 1=1
"""

PLACE_FILTER_TRANSAC = '''
    AND SK_D_Place IN {place_filter}
'''
DATE_FILTER_TRANSAC = '''
    D.Date between '{beg_date}' and '{end_date}'
'''

SQL_PLACES_ODP = """
  SELECT DISTINCT
      P.[No_Place],
      O.[DH_Deb_Permis] as deb,
      O.[DH_Fin_Permis] as fin
  FROM [Axes].[dbo].[D_PermisODP] O
  INNER JOIN Axes.dbo.D_Place P ON P.SK_D_Place = O.SK_D_Place
  WHERE 1=1
	AND O.MD_Vers_Courant = 'Oui'
    AND O.Type_Permis_ODP IN ('Capuchonner', 'Enlever')
"""

DATE_FILTER_ODP = """ O.DH_Fin_Permis >= '{beg_date}' AND O.DH_Deb_Permis <= '{end_date}'"""

PLACE_FILTER_ODP = """ AND P.SK_D_Place IN {}"""

# SQL_PLACES_ODP = """
# SELECT DISTINCT
#     a.[sNoEmplacement] as No_Place,
#     a.[dtPrevue] as deb,
#     p.dtautfin as fin
# FROM [Staging].[gsm].[S_sacActUniteUrbaine] a
#     JOIN [Staging].[gsm].S_sacLocPermis p on p.sNoPermis = a.sNoPermis
# 
# WHERE sCodeActivite IN ('P', 'E')
#     AND dtrealise IS NOT NULL
#     --AND a.Dt_Expir = '2999-12-31' AND p.Dt_Expir = '2999-12-31'
# """
# 
# DATE_FILTER_ODP = """ p.dtAutFin >= '{beg_date}' AND p.dtAutDebut <= '{end_date}'"""
# 
# PLACE_FILTER_ODP = """ AND a.sNoEmplacement IN {}"""
