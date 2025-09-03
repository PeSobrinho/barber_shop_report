import os

#Dataset path
data = './data/barbearia_datasetv2.csv'

# Database credentials
user = os.environ.get('user', 'postgres')
password = os.environ.get('password', 'tqqEMoShJYFpj0Xc')
host = os.environ.get('host', 'capably-replete-rudd.data-1.use1.tembo.io')
port = '5432'
database = os.environ.get('database', 'barber_shop')
schema='raw'
ssl_cert= './configs/ca.crt' # ssl certificate path
