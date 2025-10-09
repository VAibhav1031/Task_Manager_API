import time
from functools import wraps
from flask import request, current_app
from task_manager_api import logging

import redis
from task_manager_api.utils import too_many_requests
# from collections import defaultdict, deque


def get_redis_client():
    return redis.Redis(
        host=current_app.config["REDIS_HOST"],
        port=current_app.config["REDIS_PORT"],
        # username=current_app.config["REDIS_USER"],
        password=current_app.config["REDIS_PASSWORD"],
        decode_responses=True,
    )


# for normal testing
# redis_client = redis.Redis(
#     host="localhost",
#     port=6379,
#     decode_responses=True,
# )
#


logger = logging.getLogger(__name__)


##############################################################################################
# Trying to use the double ended queue data strucure to sliding window technique without redis
# ############################################################################################

# ip_queue = defaultdict(deque)
# def sliding_window(window_queue, window_size, limit, key_ip, arrival_time=None):
#     # i think  first  check should be the  that the currently the incoming  request can be entertained or Not
#     # why add to the deque if it is  not  valid just dont allow
#
#     if arrival_time is None:
#         arrival_time = time.time()
#
#     while window_queue and window_queue[0] <= (arrival_time - window_size):
#         window_queue.popleft()
#
#     logger.info(f"window_queue : {window_queue}")
#     if not window_queue and key_ip in window_queue:
#         del ip_queue[key_ip]
#
#     if len(window_queue) >= limit:
#         return False
#
#     window_queue.append(arrival_time)
#     return True
#
#
# def sliding_window_per_user(window_queue, window_size, limit, arrival_time):
#     # but how  we get the  username i thought , then this  came to my mind first decorator run would be the app.route one
#     # then we can use the  request function to get the username and do a sruff
#     while window_queue and window_queue[0] <= (arrival_time - window_size):
#         window_queue.popleft()
#     if len(window_queue) >= limit:
#         return False
#
#     return True


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
    redis_client = get_redis_client()
    script = redis_client.register_script(rate_limit_script)
    now = int(time.time())
    return script(keys=[key_prefix], args=[window_size, limit, now])


# PER-USER related
def record_failed_attempt(key_prefix, limit, window_size):
    redis_client = get_redis_client()
    script = redis_client.register_script(user_record_failed_attempt_script)
    now = int(time.time())
    return script(keys=[key_prefix], args=[window_size, limit, now])


def is_user_blocked(key_prefix, user_max_request):
    redis_client = get_redis_client()
    count = redis_client.zcard(key_prefix)
    return count >= user_max_request


###############


######################################
# Decorator for the per-ip rate limit
# ###################################
def rate_limit(identifier, limit, window_size):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            ip = request.headers.get("X-Forwarded-For", request.remote_addr)
            key_prefix_ip = f"{identifier}:ip:{ip}"

            logger.info(f"User ip=> {key_prefix_ip}")
            # window_queue = ip_queue[key_ip]

            # if sliding_window(window_queue, window_size, limit, key_ip):
            #     return f(*args, **kwargs)

            if not is_rate_limited(key_prefix_ip, limit, window_size):
                logger.error(f"Blocked IP : {ip} for too many request ")
                return too_many_requests(msg="Rate Limit Exceeded ::) ")

            return f(*args, **kwargs)

        return wrapper

    return decorator
