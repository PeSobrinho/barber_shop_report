from dotenv import load_dotenv
import os

load_dotenv()

user = os.getenv('user')
password = os.getenv('password')
host = os.getenv('host')
port = os.getenv('port')
database = os.getenv('database')
schema = os.getenv('schema')
ssl_cert= os.getenv('ssl_cert')