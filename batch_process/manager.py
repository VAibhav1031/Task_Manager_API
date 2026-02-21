import time 
from task_manager_api import db
from sqlalchemy import insert
from task_manager_api.models import Task
from . import bucket_,MAX_PENDING_LIMIT, GLOBAL_LIMIT, total_commit 
import batch_process
import logging
import threading
import os 
import requests



logger = logging.getLogger(__name__)

lock = threading.Lock()

go_session = requests.session()

def managing(app):
    with app.app_context():
        global bucket_, total_commit, go_session
        last_time_flush = time.time()
        while True:
            processing_data = []

            with lock:
                # last_time_flush is initialized in the __init__.py with time.time()

                # here again check bucket_ first check is for the thing like if the http request failed we made that whatever the user has requested would be in the bucket again , 
                if  bucket_  or (len(bucket_)>= GLOBAL_LIMIT or (bucket_   and ((time.time() - last_time_flush) >= MAX_PENDING_LIMIT))) : 
                    processing_data = bucket_[:]
                    bucket_.clear()
            
            if processing_data:
                try:
                    # db.session.execute(
                    #         insert(Task), 
                    #         processing_data 
                    #         )
                    # db.session.commit()

                    response = go_session.post("http://go-batcher:7676/tasks",json=processing_data,headers={"Content-Type": "application/json"})

                    if response.status_code != 202:
                        logger.error(f"Microservice failed : {response.status_code}")
                        bucket_ = processing_data[:]
                        continue

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


                        bucket_ = processing_data[:]
                        logger.error(f"Batch Http request failed error={e}")


            time.sleep(0.5)


