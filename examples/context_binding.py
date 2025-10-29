"""
Context and binding examples
"""

from mylogger import logger


def main():
    """Context binding examples"""

    # Bind context
    request_logger = logger.bind(request_id="abc123", user_id=42)
    request_logger.info("Processing request")
    request_logger.info("Request completed")

    # Use context manager
    with logger.contextualize(transaction_id="xyz789"):
        logger.info("Transaction started")
        process_transaction()
        logger.info("Transaction finished")


def process_transaction():
    """Simulate transaction processing"""
    logger.debug("Processing...")


if __name__ == "__main__":
    main()
