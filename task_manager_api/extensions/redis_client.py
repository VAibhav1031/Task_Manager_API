from redis import ConnectionPool

pool = None 

def init_redis(app):
    global pool
    pool =  ConnectionPool(
            host=app.config.get("REDIS_HOST"),
            port=app.config.get("REDIS_PORT"),
            password=app.config.get('REDIS_PASSWORD'),
            max_connections=230,  # tune this
            socket_timeout=1,
            socket_connect_timeout=1,
        )

