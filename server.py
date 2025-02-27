from fastapi import FastAPI
import uvicorn
import logging
import os

# Configure logging
logging.basicConfig(
    format='%(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/")
def root():
    """
    Root endpoint to handle default requests.
    """
    return {"message": "Service is operational."}

@app.get("/health")
def health_check():
    """
    Health check endpoint for Render's service settings.
    """
    return {"status": "healthy"}

if __name__ == "__main__":
    os.environ["LOGURU_LEVEL"] = "ERROR"
    logger.info("[INFO] Server is starting...")
    try:
        uvicorn.run(
            "server:app",
            host="0.0.0.0",
            port=10003,  # Render.com's default port
            log_level="error",  # Suppress uvicorn logs
        )
        logger.info("[INFO] Server is up and running.")
    except KeyboardInterrupt:
        logger.info("[WARNING] Server is shutting down...")
    except Exception as e:
        logger.error(f"[ERROR] {e}")
