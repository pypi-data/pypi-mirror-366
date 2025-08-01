############################################
########## Connections config ##############
############################################

# sql-server (target db, datawarehouse)
PARK_OCCUPANCY = {
    'server': 'prisqlbiprod01',
    'database': 'CPTR_Station',
    'autocommit': False,
    'driver': 'SQL Server',
}

AXES = {
    'server': 'prisqlbiprod01',
    'database': 'Axes',
    'autocommit': False,
    'driver': 'SQL Server',
}

STAGING = {
    'server': 'prisqlbiprod01',
    'database': 'Staging',
    'autocommit': False,
    'driver': 'SQL Server',
}
