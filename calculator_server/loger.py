import time


def log_processing_time(f):
    def timer(*args, **kwargs):
        start_time = time.time()
        result = f(*args, **kwargs)
        duration = time.time() - start_time
        logging.info(f"Request took {duration} to process.")
        return result
    return timer
