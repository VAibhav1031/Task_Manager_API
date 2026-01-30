import time 
from task_manager_api import db
from sqlalchemy import insert
from task_manager_api.models import Task
from . import bucket_,MAX_PENDING_LIMIT, GLOBAL_LIMIT, total_commit 
import batch_process
import logging
import threading
import os 

logger = logging.getLogger(__name__)

lock = threading.Lock()


def managing(app):
    with app.app_context():
        global bucket_, total_commit
        last_time_flush = time.time()
        while True:
            processing_data = []

            with lock:
                # last_time_flush is initialized in the __init__.py with time.time()
                if len(bucket_)>= GLOBAL_LIMIT or (bucket_   and ((time.time() - last_time_flush) >= MAX_PENDING_LIMIT)) : 
                    processing_data = bucket_[:]
                    bucket_.clear()
            
            if processing_data:
                try:
                    db.session.execute(
                            insert(Task), 
                            processing_data 
                            )
                    db.session.commit()

                    total_commit += 1 # updating the total_commit parameter (only for debugging)

                    last_time_flush = time.time()
                    
                    logger.info(f"Batch commited of {len(processing_data)} request")
                    
                    logger.info(f"worker PID : {os.getpid()}, thread ID: {threading.get_ident()}, bucket_id: {id(bucket_)}, bucket_len: {len(processing_data)}, last_time_flush : {last_time_flush}")
                    
                    logger.info(f"worker PID : {os.getpid()}, total_request: {batch_process.total_request}, total_batch_commited: {total_commit}")
                    #there is one thing like  bucket_id : cause earlier we were duing rebind (-ing ) which was literally a new object creation
                    # and referencing to that,  and in the threading , that is the worse thing to  stop your  function to run or work  
                    # now we chose the mutation. 

                except Exception as e:
                        db.session.rollback()
                        logger.error(f"Batch Task creation failed error={e}")


            time.sleep(0.5)


