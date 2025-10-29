"""
Advanced logging patterns
"""

from mylogger import logger
import time

def request_tracking():
    """Track request with unique ID"""
    import uuid
    
    request_id = str(uuid.uuid4())
    req_logger = logger.bind(request_id=request_id)
    
    req_logger.info("Request started")
    time.sleep(0.1)
    req_logger.info("Request processed")
    req_logger.success("Request completed")


def performance_logging():
    """Log performance metrics"""
    start = time.time()
    
    # Do some work
    time.sleep(0.5)
    
    duration = time.time() - start
    logger.info("Operation completed", duration_ms=f"{duration*1000:.2f}")


def main():
    """Advanced pattern examples"""
    
    request_tracking()
    performance_logging()


if __name__ == "__main__":
    main()
