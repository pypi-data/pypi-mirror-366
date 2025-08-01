TRANSACTION_SQL = """
SELECT [SK_F_Trx_Pl]
      ,[SK_D_Place]
      ,[SK_D_Date]
      ,[SK_R_MethodePaiement]
      ,[No_Place]
      ,[No_Trans_Src]
      ,[DH_Debut_Prise_Place]
      ,[DH_Fin_Prise_Place]
FROM [CPTR_Station].[dbo].[F_TransactionPayezPartez]
WHERE 1=1
{whr_cond}
"""

PLACE_FILTER_TRANSAC = '''
    AND No_Place IN {place_filter}
'''
DATE_FILTER_TRANSAC = '''
     DH_Debut_Prise_Place <= '{to}' AND DH_Fin_Prise_Place >= '{from}'
'''

      #--,case when  cast(DH_Debut_Prise_Place as date) = '{date}' then DH_Debut_Prise_Place  else cast('{date}' as datetime) end                                   as debutReel
      #--,case when  cast(DH_Fin_Prise_Place as date) = '{date}' then DH_Fin_Prise_Place  else dateadd(minute, -1,cast(dateadd(day, 1,'{date}') as datetime)) end   as finReel