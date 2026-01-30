# from . import bucket_,  total_request
import batch_process
import logging
logger = logging.getLogger(__name__)
import threading

def bucket_insertion(data,user_id):
    # for the /api/v1/tasks POST 
    data["user_id"] = user_id

    lock = threading.Lock()
    with lock:
        batch_process.total_request += 1
        batch_process.bucket_.append(data)

    # logging.info(f"total_request->{total_request}")

