import time
from redis.exceptions import RedisError,ConnectionError
import redis 
from task_manager_api import db
from sqlalchemy import insert
from task_manager_api.models import Task
from . import bucket_,MAX_PENDING_LIMIT, GLOBAL_LIMIT, total_commit 
import batch_process
import logging
import threading
import os 
import requests
from requests.adapters import HTTPAdapter
import orjson
from task_manager_api.extensions.redis_client import pool
from redis import Redis

logger = logging.getLogger(__name__)

lock = threading.Lock()

go_session = requests.session()
adapter = HTTPAdapter(pool_connections=75, pool_maxsize=110)
go_session.mount("http://",adapter)

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
                # last_time_flush is initialized in the __init__.py with time.time()

                # here again check bucket_ first check is for the thing like if the http request failed we made that whatever the user has requested would be in the bucket again , 
                if  len(bucket_)>= GLOBAL_LIMIT or (bucket_   and ((time.time() - last_time_flush) >= MAX_PENDING_LIMIT)) : 
                    processing_data = bucket_[:]
                    bucket_.clear()
            
            if processing_data:
                try:
                    # db.session.execute(
                    #         insert(Task), 
                    #         processing_data 
                    #         )
                    # db.session.commit()

                    # payload = orjson.dumps(processing_data)
                    # response = go_session.post("http://go-batcher:7676/tasks",data=payload,headers={"Content-Type": "application/json"})

                    #
                    #
                    # if response.status_code != 202:
                    #     logger.error(f"Microservice failed : {response.status_code}")
                    #     with lock:
                    #         processing_data.extend(bucket_)
                    #         bucket_.clear()
                    #         bucket_.extend(processing_data)
                    #     continue

                    payload_batch =  [orjson.dumps(task) for task in processing_data]

                    try:
                        redis_client.lpush("task_queue", *payload_batch)
                    except (ConnectionError,RedisError) as e:
                        logger.error(f"REDIS IS DOWN!, saving data to emergency file ..., error {e}")
                        emergency_fallback(*payload_batch)


                    total_commit += 1 # updating the total_commit parameter (only for debugging)
                    last_time_flush = time.time()
                    logger.info(f"Batch commited of {len(processing_data)} request")
                    
                    logger.info(f"worker PID : {os.getpid()}, thread ID: {threading.get_ident()}, bucket_id: {id(bucket_)}, bucket_len: {len(processing_data)}, last_time_flush : {last_time_flush}")
                    
                    logger.info(f"worker PID : {os.getpid()}, total_request: {batch_process.total_request}, total_batch_commited: {total_commit}")
                    #there is one thing like  bucket_id : cause earlier we were duing rebind (-ing ) which was literally a new object creation
                    # and referencing to that,  and in the threading , that is the worse thing to  stop your  function to run or work  
                    # now we chose the mutation. 

                except Exception as e:
                        # db.session.rollback()
                        # logger.error(f"Batch Task creation failed error={e}")
             #
             #        with lock:
             #            processing_data.extend(bucket_)
             #            bucket_.clear()
             #            bucket_.extend(processing_data)
             # # for saving the data na if any error occur brother (if any error will occur system will not work noones data will be sent unless it get recover or  restart nothing else why this so that user dont push another data again , it is longterm protection
                        logger.error(f"Batch redis push to queue failed , error={e}")
             #

            time.sleep(0.01)


