import sys
import signal
import logging
import time
import socket
from portfolio_server.server import create_mcp_server
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("portfolio_mcp")

# Valid transport types
VALID_TRANSPORTS = ["stdio", "sse", "http"]

# Transport-specific configuration
TRANSPORT_CONFIG = {
    "stdio": {
        "startup_delay": 0.1,  # Short delay for stdio
        "max_retries": 1,      # No retries needed for stdio
        "retry_delay": 0.5,    # Delay between retries
    },
    "sse": {
        "startup_delay": 3.0,  # Increased delay for SSE to establish connection
        "max_retries": 5,      # Increased retries for network transports
        "retry_delay": 3.0,    # Increased delay between retries
        "port": 8081,          #8 Default SSE port
        "connection_timeout": 10.0  # Added timeout for connection attempts
    },
    "http": {
        "startup_delay": 0.5,
        "max_retries": 3,
        "retry_delay": 1.0,
        "port": 8000,          # Default HTTP port
    }
}

# Global flag for shutdown
is_shutting_down = False

# 健康监听
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/health"):
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"ok")
        else:
            self.send_response(404)
            self.end_headers()

def run_health_server(port=8080):
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    server.serve_forever()

# 在入口启动健康检查守护线程（不会阻塞主服务，也不会中断 FastMCP 业务）
threading.Thread(target=run_health_server, args=(8080,), daemon=True).start()


# Signal handlers for graceful shutdown
def handle_shutdown_signal(signum, frame):
    global is_shutting_down
    if is_shutting_down:
        logger.warning("Forced shutdown triggered")
        sys.exit(1)
    
    logger.info(f"Shutdown signal received ({signum}), stopping server gracefully...")
    is_shutting_down = True
    # Note: The actual shutdown happens in the main loop

# Register signal handlers
signal.signal(signal.SIGINT, handle_shutdown_signal)
signal.signal(signal.SIGTERM, handle_shutdown_signal)

# Create the MCP server at module level
try:
    mcp = create_mcp_server()
    logger.info("MCP server created successfully")
except Exception as e:
    logger.error(f"Failed to create MCP server: {e}")
    sys.exit(1)

def validate_transport(transport_type):
    """Validate that the transport type is supported."""
    if transport_type not in VALID_TRANSPORTS:
        logger.error(f"Invalid transport type: {transport_type}. Valid options are: {', '.join(VALID_TRANSPORTS)}")
        return False
    return True


def check_connection_status(transport_type, config=None):
    """Check the connection status for the specified transport."""
    if config is None:
        config = {}

    if transport_type == "stdio":
        # stdio should always be available
        return True
    elif transport_type == "sse" or transport_type == "http":
        # Check if the port is available for sse/http
        port = config.get("port", TRANSPORT_CONFIG[transport_type]["port"])
        try:
            # Try to bind to the port to see if it's available
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            
            # If the connection was refused, the port is available (good)
            # If we could connect, someone else is using it (bad for our server)
            return result != 0
        except Exception as err:
            logger.warning(f"Error checking connection status for {transport_type}: {err}")
            return False
    else:
        logger.warning(f"Unknown transport type for status check: {transport_type}")
        return False


def run_server_with_retry(transport_type, config=None):
    """Run the server with retry logic if the connection fails."""
    if config is None:
        config = {}

    # Get transport configuration
    transport_config = TRANSPORT_CONFIG.get(transport_type, {})
    max_retries = config.get("max_retries", transport_config.get("max_retries", 1))
    retry_delay = config.get("retry_delay", transport_config.get("retry_delay", 1.0))
    startup_delay = config.get("startup_delay", transport_config.get("startup_delay", 0.5))

    # Wait before starting to allow connections to establish
    logger.info(f"Waiting {startup_delay}s before starting server...")
    time.sleep(startup_delay)

    # Check connection status
    if not check_connection_status(transport_type, config):
        logger.warning(f"Transport {transport_type} may not be available. Proceeding with caution.")

    # Initialize retry counter
    retries = 0
    last_error = None

    while retries <= max_retries:
        try:
            # Create transport options
            transport_options = {}
            
            # Add transport-specific options
            if transport_type == "sse" or transport_type == "http":
                port = config.get("port", transport_config.get("port"))
                transport_options["port"] = port
            
            # Run the server with the configured transport and options
            logger.info(f"Starting server with {transport_type} transport (attempt {retries + 1}/{max_retries + 1})...")
            mcp.run(transport=transport_type, **transport_options)
            
            # If we get here, the server started successfully
            return True
        except ConnectionError as connect_err:
            # Specific handling for connection errors
            last_error = connect_err
            logger.error(f"Connection error starting server: {connect_err}")
        except OSError as os_err:
            # Handle OS errors like port already in use
            last_error = os_err
            logger.error(f"OS error starting server: {os_err}")
        except Exception as err:
            # Catch any other exceptions
            last_error = err
            logger.error(f"Error starting server: {err}")

        # Increment retry counter
        retries += 1
        
        if retries <= max_retries:
            logger.info(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)

    # If we get here, all retries failed
    logger.error(f"Failed to start server after {max_retries + 1} attempts. Last error: {last_error}")
    return False

def main():
    """Main entry point for the portfolio server."""
    logger.info("Portfolio Manager MCP Server starting")

    # Default
    transport = "stdio"
    config = {}

    # Check command line arguments for transport type
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg == "--sse":
                transport = "sse"
            elif arg.startswith("--transport="):
                transport = arg.split("=")[1]
            elif arg.startswith("--port="):
                try:
                    config["port"] = int(arg.split("=")[1])
                except ValueError:
                    logger.error(f"Invalid port number: {arg.split('=')[1]}")
                    sys.exit(1)
            elif arg.startswith("--retry="):
                try:
                    config["max_retries"] = int(arg.split("=")[1])
                except ValueError:
                    logger.error(f"Invalid retry count: {arg.split('=')[1]}")
                    sys.exit(1)

    # Validate transport type
    if not validate_transport(transport):
        sys.exit(1)

    logger.info(f"Starting MCP server with transport: {transport}")
    if config:
        logger.info(f"Transport configuration: {config}")

    try:
        # For SSE transport, use the dedicated SSE module
        if transport == "sse":
            from portfolio_server.sse import run_sse_server
            port = config.get("port", TRANSPORT_CONFIG["sse"]["port"])
            host = "0.0.0.0"  # Default host
            logger.info(f"Starting SSE server on {host}:{port}")
            run_sse_server(port=port, host=host)
        else:
            # For other transports, use the standard retry logic
            success = run_server_with_retry(transport, config)
            if not success:
                logger.error("Failed to start the server after all attempts.")
                sys.exit(1)
    except KeyboardInterrupt:
        # Handle keyboard interrupt (Ctrl+C)
        logger.info("Server interrupted via keyboard")
    except Exception as err:
        # Handle any other exceptions
        logger.error(f"Error running MCP server: {err}")
        sys.exit(1)
    finally:
        # Perform cleanup
        logger.info("Shutting down MCP server...")
        # Add any necessary cleanup code here
        logger.info("MCP server shutdown complete")

if __name__ == "__main__": 
    main()