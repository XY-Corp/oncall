from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
import ssl

connect = None
DictCursor = None
IntegrityError = None


def init(config):
    global connect
    global DictCursor
    global IntegrityError

    conn_kwargs = config['conn']['kwargs']

    query_params = {'charset': conn_kwargs.get('charset', 'utf8')}
    if 'unix_soccet' in con_kwargs:
        query_params['unix_socket'] = conn_kwargs['unix_socket']

    url = URL.create(
        drivername=conn_kwargs['scheme'],
        username=conn_kwargs['user'],
        password=conn_kwargs['password'],
        host=conn_kwargs.get('host'),
        port=conn_kwargs.get('port'),
        database=conn_kwargs['database'],
        query=query_params
    )

    connect_args = {}
    if config['conn'].get('use_ssl'):
        ssl_ctx = ssl.create_default_context()
        connect_args["ssl"] = ssl_ctx

    engine = create_engine(
        url,
        connect_args=connect_args,
        **config['kwargs']
    )

    dbapi = engine.dialect.dbapi
    IntegrityError = dbapi.IntegrityError

    DictCursor = dbapi.cursors.DictCursor
    connect = engine.raw_connection
