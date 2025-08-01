import pandas as pd
import numpy as np
from numba import jit
from sqlalchemy.engine.base import Engine
from sqlalchemy import create_engine

def getEngine(server, database, driver, Trusted_Connection='yes', autocommit=True, fast_executemany=True):
    """ Create a connection to a sql server via sqlalchemy
    Arguments:
    server -- The server name (str). e.g.: 'SQL2012PROD03'
    database -- The specific database within the server (str). e.g.: 'LowFlows'
    driver -- The driver to use for the connection (str). e.g.: SQL Server
    trusted_conn -- Is the connection to be trusted. Values are 'yes' or 'No' (str).
    """

    if driver == 'SQL Server':
        engine = create_engine(
            f"mssql+pyodbc://{server}/{database}"
            f"?driver={driver}"
            f"&Trusted_Connection={Trusted_Connection}"
            f"&autocommit={autocommit}",
            fast_executemany=fast_executemany
        )
    else:
        raise NotImplementedError('No other connections supported')
    return engine


def get_data(con, sql, place_sql="", date_sql="", place_filter=None,
             date_filter=None, execute_only=False):
    """ TODO

    Returns
    -------
    data: pandas.DataFrame
        Return the data querried by the SQL script.
    """

    con = con if isinstance(con, Engine) else getEngine(**con)
    sk_d_place = place_filter
    period = date_filter

    whr_cond = place_sql.format(place_filter=sk_d_place) if sk_d_place else ""

    whr_cond += ' AND (' + date_sql.format(**period) + ')' if date_sql else ""

    if date_filter:
        sql = sql.format(whr_cond=whr_cond, **period)
    else:
        sql = sql.format(whr_cond=whr_cond)

    if execute_only:
        con.execute(sql)
        return None

    data = pd.read_sql(con=con, sql=sql)
    return data

@jit(nopython=True)
def _to_hour_bin(a):
    """ TODO
    """

    #create new temp cupy array b to contain minute duration per hour.
    b = np.zeros((len(a),24))
    for j in range(0,len(a)):
        hours = int((a[j][0]/3600)+(a[j][1]/60))
        if(hours==0): # within same hour
            b[j][a[j][3]] = int(a[j][0]/60)
        elif(hours==1): #you could probably delete this condition.
            b[j][a[j][3]] = 60-a[j][1]
            b[j][a[j][4]] = a[j][2]
        else:
            b[j][a[j][3]] = 60-a[j][1]
            if(hours<24): #all array elements will be all 60 minutes if durationa is over 24 hours
                if(a[j][3]+hours<24):
                    b[j][a[j][3]+1:a[j][3]+hours]=60
                    b[j][a[j][4]] = a[j][2]
                else:
                    b[j][a[j][3]+1:24]=60
                    b[j][0:(a[j][3]+1+hours)%24]=60
                    b[j][a[j][4]] = a[j][2]

    return b

def from_transaction_to_hour_bin(data, column_deb='DH_Debut_Prise_Place', column_fin='DH_Fin_Prise_Place'):
    """ TODO
    """

    #If your duration goes over 24 hours total, ALL hour column values will be all 60 minutes.
    df = data.copy()
    df.rename(columns={column_deb:'sta', column_fin:'end'}, inplace=True)

    #the object is a string, so let's convert it to date time
    df['sta']= df['sta'].astype('datetime64[s]')
    df['end']=df['end'].astype('datetime64[s]')

    df['dur']=((df['end']-df['sta']).view('int64') / (10**9)).astype('int64')

    #create new df of same type to convert to cupy (to preserve datetime values)
    df2=pd.DataFrame()
    df2['dur']=((df['end']-df['sta']).view('int64') / (10**9)).astype('int64')
    df2['min_sta'] =df['sta'].dt.minute.view('int64')
    df2['min_end']= df['end'].dt.minute.view('int64')
    df2['h_sta']= df['sta'].dt.hour.view('int64')
    df2['h_end']= df['end'].dt.hour.view('int64')
    df2['day']=df['sta'].dt.day.view('int64')

    #convert df2's values from df to numpy array
    a = df2.to_numpy()

    # bring cupy array b back to a df.
    b = _to_hour_bin(a)
    cpdf = pd.DataFrame(b, columns=['Hr00', 'Hr01', 'Hr02', 'Hr03', 'Hr04',
                                    'Hr05', 'Hr06', 'Hr07', 'Hr08', 'Hr09',
                                    'Hr10', 'Hr11', 'Hr12', 'Hr13','Hr14',
                                    'Hr15', 'Hr16', 'Hr17', 'Hr18', 'Hr19',
                                    'Hr20', 'Hr21', 'Hr22','Hr23'])

    #concat the original and cupy df
    df = pd.concat([df, cpdf], axis=1)

    return df
