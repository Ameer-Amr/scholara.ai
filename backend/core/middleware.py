import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# Define standard ANSI escape sequences for terminal colors
CLR_GREEN = "\033[92m"   # Incoming requests
CLR_CYAN = "\033[96m"    # Successful responses
CLR_RED = "\033[91m"     # Crashes / Errors
CLR_RESET = "\033[0m"    # Clear formatting back to default text

class ScholaraColorFormatter(logging.Formatter):
    """Custom logging formatter that paints the entire message line based on severity level."""
    
    def format(self, record):
        # Format the base timestamp and level name layout
        log_fmt = f"%(asctime)s [%(levelname)s] "
        
        # Pick the color based on the log level
        if record.levelno == logging.ERROR:
            log_fmt += f"{CLR_RED}%(message)s{CLR_RESET}"
        elif "-->" in record.getMessage():
            log_fmt += f"{CLR_GREEN}%(message)s{CLR_RESET}"
        else:
            log_fmt += f"{CLR_CYAN}%(message)s{CLR_RESET}"
            
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)

# Configure the stream handler for Docker console output
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(ScholaraColorFormatter())

# Set up the isolated custom logger
logger = logging.getLogger("scholara_request_logger")
logger.setLevel(logging.INFO)
logger.addHandler(stream_handler)
logger.propagate = False 


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        method = request.method
        url = request.url.path
        client_host = request.client.host if request.client else "unknown"
        
        # Will print completely GREEN
        logger.info(f"--> Incoming request: {method} {url} from {client_host}")
        
        try:
            response = await call_next(request)
            process_time = (time.time() - start_time) * 1000
            
            # Will print completely CYAN
            logger.info(
                f"<-- Outgoing response: {method} {url} | "
                f"Status: {response.status_code} | "
                f"Duration: {process_time:.2f}ms"
            )
            return response    
        except Exception as e:
            process_time = (time.time() - start_time) * 1000
            # Will print completely RED
            logger.error(
                f"X-- Request Failed: {method} {url} | "
                f"Error: {str(e)} | "
                f"Duration: {process_time:.2f}ms"
            )
            raise e