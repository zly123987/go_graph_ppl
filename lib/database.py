import os
import configparser
from utils.useful_tools.ip import get_host_ip
runPath = os.path.dirname(os.path.realpath(__file__))


class DatabaseConnection:
    def __init__(self, *args, **kwargs):
        self.host = kwargs.get('host')
        self.port = kwargs.get('port')
        self.db = kwargs.get('db')
        self.user = kwargs.get('user')
        self.password = kwargs.get('password')
        self.auth_source = kwargs.get('auth_source')


def get_internal_ip():
    config = configparser.ConfigParser()
    config.read(os.path.join(runPath.split('/lib')[0], 'Config/configuration.ini'))
    internal = {}

    try:
        internal = config['InternalIP']
        return internal['IP']
    except:
        print('No Postgres Database config found, will use defaults')
        return get_host_ip()



    return DatabaseConnection(**connection)

def get_postgres_connection():
    config = configparser.ConfigParser()
    config.read(os.path.join(runPath.split('/lib')[0], 'Config/configuration.ini'))
    postgres = {}

    try:
        postgres = config['Postgres']
    except:
        print('No Postgres Database config found, will use defaults')

    connection = {
        'host': postgres.get('POSTGRES_HOST', '192.168.1.16'),
        'port': postgres.get('POSTGRES_PORT', '5432'),
        'db': postgres.get('POSTGRES_DB', 'cvetriage'),
        'user': postgres.get('POSTGRES_USER', 'cvetriage'),
        'password': postgres.get('POSTGRES_PASSWORD', 'postgres')
    }

    return DatabaseConnection(**connection)


def get_mongo_connection():
    config = configparser.ConfigParser()
    config.read(os.path.join(runPath.split('/lib')[0], 'Config/configuration.ini'))
    mongo = {}

    try:
        mongo = config['Mongodb']
    except:
        print('No Mongo Database config found, will use defaults')

    # For mongo host and port, check env vars if not in config
    mongo_host, mongo_port = get_host_ip(), '27019'
    if 'MONGODB_PORT' in os.environ and os.environ['MONGODB_PORT']:
        mongo_port = os.environ['MONGODB_PORT']
    if 'MONGODB_HOST' in os.environ and os.environ['MONGODB_HOST']:
        mongo_host = os.environ['MONGODB_HOST']

    connection = {
        'host': mongo.get('MONGODB_HOST', mongo_host),
        'port': int(mongo.get('MONGODB_PORT', mongo_port)),
        'db': mongo.get('MONGO_DB_NAME', 'library-crawler'),
        'user': mongo.get('User', ''),
        'password': mongo.get('Password', ''),
        'auth_source': mongo.get('AuthSource', '')
    }
    return DatabaseConnection(**connection)

def get_neo4j_connection():
    config = configparser.ConfigParser()
    print(runPath)
    print(os.path.join(runPath.split('/lib')[0], 'Config/configuration.ini'))
    config.read(os.path.join(runPath.split('/lib')[0], 'Config/configuration.ini'))
    neo4j = {}

    try:
        neo4j = config['Neo4j']
    except:
        print('No Mongo Database config found, will use defaults')
    connection = {
        'host':neo4j.get('Host', 'localhost'),
        'port': int(neo4j.get('Port', '7687')),
        'db': neo4j.get('DB', ''),
        'user': neo4j.get('User', 'neo4j'),
        'password': neo4j.get('Password', '1234')
    }
    return DatabaseConnection(**connection)
