import pandas as pd
from sqlalchemy import types, create_engine

###################################################
### Start: DB connection strings config
###################################################

HOST = 'host-scan'
SERVICE_NAME = 'domain.com'

tns = """
    (DESCRIPTION =
         (ADDRESS = (PROTOCOL = TCP)(HOST = %s)(PORT = 1521))
         (CONNECT_DATA =
          (SERVER = DEDICATED)
          (SERVICE_NAME = %s)
          )
    )
""" % (HOST, SERVICE_NAME)
    
usr = ''
pwd = ''

###################################################
### End: DB connection strings config
###################################################

###################################################
### Start: Prepare pandas DataFrame
###################################################

pathToExcelFile = ''
sheetname = ''

df = pd.read_excel(pathToExcelFile, sheetname = sheetname)

newColumnNames = []

df = df.iloc[:,:len(newColumnNames)]
df.columns = newColumnNames

def remove_non_ascii(row):
    return [''.join([i if ord(i) < 128 else ' ' for i in r]) for r in row]

str_cols = df.columns[df.dtypes == 'object'].tolist()

df.loc[:,str_cols] = df[str_cols].apply(remove_non_ascii)

dtyp = {c:types.VARCHAR(df[c].str.len().max())
    for c in df.columns[df.dtypes == 'object'].tolist()}

###################################################
### End: Prepare pandas DataFrame
###################################################

###################################################
### Start: Write pandas DataFrame to Oracle
###################################################

SCHEMA = ''

TABLE_NAME = ''

engine = create_engine('oracle+cx_oracle://%s:%s@%s' % (usr, pwd, tns))

df.to_sql(name = TABLE_NAME, con = engine, schema = SCHEMA,
          if_exists = 'replace', index = False, dtype = dtyp)