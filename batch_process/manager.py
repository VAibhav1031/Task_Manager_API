import time
from redis.exceptions import RedisError,ConnectionError
from . import bucket_,MAX_PENDING_LIMIT, GLOBAL_LIMIT, total_commit 
import batch_process
import logging
import threading
import os 
import orjson
from task_manager_api.extensions.redis_client import pool
from redis import Redis

logger = logging.getLogger(__name__)

lock = threading.Lock()

redis_client = Redis(connection_pool=pool,decode_responses=True)


def emergency_fallback(payload_bytes ):
    try:
        with open("/task_app/emergency_fallback.jsonl","ab") as f:
            f.write(payload_bytes)
            f.write(b"\n")
        logger.info("Batch saved to local disk sucessfully")

    except Exception as e: 
        logger.critical(f"TOTAL SYSTEM FAILURE: could not saved to disk : {e}")


def managing(app):
    with app.app_context():
        global bucket_, total_commit, go_session
        last_time_flush = time.time()
        while True:
            processing_data = []

            with lock:
                
                if  len(bucket_)>= GLOBAL_LIMIT or (bucket_   and ((time.time() - last_time_flush) >= MAX_PENDING_LIMIT)) : 
                    processing_data = bucket_[:]
                    bucket_.clear()
            if processing_data:
                try:


                    payload_batch =  [orjson.dumps(task) for task in processing_data]

                    try:
                        redis_client.lpush("task_queue", *payload_batch)
                    except (ConnectionError,RedisError) as e:
                        logger.error(f"REDIS IS DOWN!, saving data to emergency file ..., error {e}")
                        emergency_fallback(*payload_batch)


                    total_commit += 1 # updating the total_commit parameter (only for debugging)
                    last_time_flush = time.time()
                    logger.info(f"Batch commited of {len(processing_data)} request")
                    #
                    logger.info(f"worker PID : {os.getpid()}, total_request: {batch_process.total_request}, total_batch_commited: {total_commit}")
                    #there is one thing like  bucket_id : cause earlier we were duing rebind (-ing ) which was literally a new object creation
                    # and referencing to that,  and in the threading , that is the worse thing to  stop your  function to run or work  
                    # now we chose the mutation. 

                except Exception as e:

                        logger.error(f"Batch redis push to queue failed , error={e}")
             

            time.sleep(0.01)


