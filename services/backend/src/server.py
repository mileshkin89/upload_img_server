"""
server.py

This module manages the initialization and execution of one or more HTTP servers using Python's
built-in `http.server` and `multiprocessing` modules.

It is designed for development or lightweight production use, where each worker process
runs an independent instance of the HTTP server on a dedicated port.

Key features:
- Launches multiple worker processes on separate ports.
- Uses a custom HTTPHandler to manage incoming requests.
- Logs server start and worker process details.
"""
from http.server import HTTPServer
from multiprocessing import Process, current_process
from handlers.http_handler import HTTPHandler
from settings.config import config
from settings.logging_config import get_logger


logger = get_logger(__name__)


def run_server_on_port(port: int):
    """
    Starts an HTTP server instance on the specified port.

    This function is intended to be run inside a separate process.
    It sets the process name for clarity and begins serving HTTP requests indefinitely.

    Args:
        port (int): The port number on which the server will listen.

    Side Effects:
        - Starts a blocking HTTP server on the given port.
        - Logs server startup information.
    """
    current_process().name = f"worker-{port}"
    logger.info(f"Starting server on http://0.0.0.0:{port}")
    server = HTTPServer(("0.0.0.0", port), HTTPHandler)
    server.serve_forever()


def run(workers: int = 1, start_port: int = 8000):
    """
    Launches multiple HTTP server worker processes.

    Each worker runs on a separate port, starting from `start_port` and incrementing
    for each additional worker. Ideal for development or parallel request testing.

    Args:
        workers (int): Number of worker processes to spawn.
        start_port (int): The base port number to start servers on.

    Side Effects:
        - Spawns one or more subprocesses running HTTP servers.
        - Logs which worker starts on which port.
    """
    for i in range(workers):
        port = start_port + i
        p = Process(target=run_server_on_port, args=(port,))
        p.start()
        logger.info(f"Worker {i + 1} started on port {port}")


if __name__ == '__main__':
    run(workers=config.WEB_SERVER_WORKERS, start_port=config.WEB_SERVER_START_PORT)