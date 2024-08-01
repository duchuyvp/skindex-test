import logging

from chat_service.entrypoints.rest import app as rest_app

logger = logging.getLogger("user_service")


def main():
    try:
        logger.info("Init application")
        rest_app.run()
    finally:
        logger.info("Application shutdown gracefully")


if __name__ == "__main__":
    main()
