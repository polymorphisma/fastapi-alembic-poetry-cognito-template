from fastapi import Request
from fastapi.responses import JSONResponse
import traceback
from app.utilities.logger import logger
import os
from dotenv import load_dotenv

load_dotenv()

# Determine environment
environment = os.getenv("ENVIRONMENT", "development")
development = environment == "development"


async def application_level_error(request: Request, call_next):
    try:
        # Proceed with the request
        response = await call_next(request)
        return response
    except Exception as exp:
        # Log the full traceback for debugging in development
        if development:
            error_details = traceback.format_exc()
            logger.error(f"An error occurred while processing the request: {str(exp)}.")
            logger.error("------------------------------------traceback------------------------------------")
            logger.error(error_details)
            logger.error("---------------------------------------------------------------------------------")

        # Return a JSON error response to the client
        return JSONResponse(
            {
                "success": False,
                "message": "An unexpected error occurred while processing your request. "
                           "Our team has been notified and is working to resolve the issue. "
                           "Please try again later."
            },
            status_code=500
        )
