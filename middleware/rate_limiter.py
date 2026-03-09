import time
from functools import wraps
from flask import request, current_app
from task_manager_api import logging
from task_manager_api.utils import decode_access_token
from task_manager_api.extensions.redis_client import pool
from task_manager_api.error_handler import too_many_requests
from redis import Redis
# from collections import defaultdict, deque

# This is the biggest culprit in the game , it cause the new connection for each get_redis_client, which cause the TCP connection to be exhausted becasue OS  just ran off the ephemeral ports ,  and under Heavy load this thing only come to know . 

# def get_redis_client():
#     return redis.Redis(
#         host=current_app.config["REDIS_HOST"],
#         port=current_app.config["REDIS_PORT"],
#         # username=current_app.config["REDIS_USER"],
#         password=current_app.config["REDIS_PASSWORD"],
#         decode_responses=True,
#     )
#

# for normal testing
# redis_client = redis.Redis(
#     host="localhost",
#     port=6379,
#     decode_responses=True,
# )
#


logger = logging.getLogger(__name__)



rate_limit_script = """
local key = KEYS[1]
local window = tonumber(ARGV[1])
local max_request = tonumber(ARGV[2])
local now = tonumber(ARGV[3])

redis.call('ZREMRANGEBYSCORE',key,0,now-window)
local count =  redis.call('ZCARD',key)

if count >= max_request then return 0  end

redis.call('ZADD',key,now,now)
redis.call('EXPIRE', key,window+10)

return 1 -- return True when we can accept the request
"""

user_record_failed_attempt_script = """
local key = KEYS[1]
local window = tonumber(ARGV[1])
local max_request = tonumber(ARGV[2])
local now = tonumber(ARGV[3])

redis.call('ZREMRANGEBYSCORE',key,0,now-window)
redis.call('ZADD',key, now, now) -- add the user because it is for the failed attempt
redis.call('EXPIRE', key,window+10)

"""


# PER-IP related
def is_rate_limited(key_prefix, limit, window_size):
    redis_client = Redis(connection_pool=pool,decode_responses=True)
    script = redis_client.register_script(rate_limit_script)
    now = int(time.time())
    return script(keys=[key_prefix], args=[window_size, limit, now])


# PER-USER related
def record_failed_attempt(key_prefix, limit, window_size): 

    redis_client = Redis(connection_pool=pool,decode_responses=True)
    script = redis_client.register_script(user_record_failed_attempt_script)
    now = int(time.time())
    return script(keys=[key_prefix], args=[window_size, limit, now])


def is_user_blocked(key_prefix, user_max_request):

    redis_client = Redis(connection_pool=pool,decode_responses=True)
    count = redis_client.zcard(key_prefix)
    return count >= user_max_request


###############


######################################
# Decorator for the user-id rate limit
# ###################################

def rate_limit(identifier, limit, window_size):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # token is used cause they are already verified 
            token = request.headers.get("Authorization").split(" ")[1]
            user_id = decode_access_token(token)

            key_prefix_user_id = f"{identifier}:user_id:{user_id}"

            logger.info(f"User-Id=> {key_prefix_user_id}")

            # if sliding_window(window_queue, window_size, limit, key_ip):
            #     return f(*args, **kwargs)

            if not is_rate_limited(key_prefix_user_id, limit, window_size):
                logger.error(f" Blocked user_id : {user_id} for too many request ")
                return too_many_requests(msg="Rate Limit Exceeded ::) ")

            return f(*args, **kwargs)

        return wrapper

    return decorator
