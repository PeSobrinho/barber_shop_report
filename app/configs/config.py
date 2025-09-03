from dotenv import load_dotenv
import os

load_dotenv()

data = os.getenv('data')

user = os.getenv('user')
password = os.getenv('password')
host = os.getenv('host')
port = os.getenv('port')
database = os.getenv('database')
schema = os.getenv('schema')
#ssl_cert= os.getenv('ssl_cert')