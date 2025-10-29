from .my_file import my_function
from mylogger import logger

if __name__ == "__main__":
    #my_function()

    # That's it! The logger is pre-configured with a file handler.
    # Logs automatically go to logs/app.log with rotation, compression, and retention.

    logger.info("Application started")
    logger.success("Operation completed")
    logger.error("Something went wrong")