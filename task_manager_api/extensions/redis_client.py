from redis import Redis

redis_client = None 

def init_redis(app):
    global redis_client

    redis_client =  Redis(
            host=app.config.get("REDIS_HOST"),
            port=app.config.get("REDIS_PORT"),
            password=app.config.get('REDIS_PASSWORD'),
            decode_responses=True,
            max_connections=100,  # tune this
            socket_timeout=1,
            socket_connect_timeout=1,
        )

