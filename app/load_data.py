import psycopg2
from sqlalchemy import create_engine
import pandas as pd
from configs import config

def load_data(path, user, password, host, port, database, schema):

    today = pd.Timestamp.now()

    engine = create_engine(f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}?sslmode=require&channel_binding=require')

    print(f'Carregando: {path} na base {database}, schema {schema}')
    df = pd.read_csv(path)

    df['data_carga'] = today

    df.to_sql('source_barbearia_dataset', index=False, con=engine, schema=schema, if_exists='replace')
    print(f'Carga concluida em {today}')

if __name__ == '__main__':

    user = config.user
    password = config.password
    host = config.host
    port = config.port
    database = config.database
    #ssl_cert= config.ssl_cert
    schema = 'raw'

    path = config.data

    load_data(
        path = path, 
        user = user, 
        password = password, 
        host = host, 
        port = port, 
        database = database, 
        #ssl_cert = ssl_cert, 
        schema = schema)

    