"""
Custom handler examples
"""

from mylogger import logger

def custom_log_function(message):
    """Custom function to handle logs"""
    print(f"[CUSTOM] {message}")


def main():
    """Custom handler examples"""
    
    # Add custom function as handler
    logger.add(custom_log_function, level="WARNING")
    
    logger.info("This goes to default handlers")
    logger.warning("This goes to custom handler too")
    logger.error("This also goes to custom handler")


if __name__ == "__main__":
    main()
