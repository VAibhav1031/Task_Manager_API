import time 

# global limit for the bucket
GLOBAL_LIMIT  = 300 
bucket_ = []
MAX_PENDING_LIMIT = 20
last_time_flush = time.time() 
total_request = 0
total_commit = 0
