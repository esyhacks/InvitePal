import time
import os
from dotenv import load_dotenv
import requests
import logging

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    format='[%(levelname)s] %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Constants
SERVER_URL = os.getenv("SERVER_URL")  # Using root endpoint
PING_INTERVAL = 300  # Ping every 5 minutes (600 seconds)

def ping_server():
    """
    Function to ping the server and log the response.
    """
    try:
        response = requests.get(SERVER_URL, timeout=30)
        if response.status_code == 200:
            logger.info("Server is operational.")
        else:
            logger.warning(f"Unexpected response from server: {response.status_code}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to ping server: {e}")

def main():
    """
    Main function to continuously ping the server at regular intervals.
    """
    logger.info("Keepalive service started.")
    time.sleep(PING_INTERVAL)  # Skip the first ping by waiting first
    while True:
        ping_server()
        time.sleep(PING_INTERVAL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Keepalive service terminated by user.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
