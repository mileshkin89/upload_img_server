
from http.server import HTTPServer
from multiprocessing import Process, current_process
from handlers.http_handler import HTTPHandler
from settings.config import config
from settings.logging_config import get_logger


logger = get_logger(__name__)


def run_server_on_port(port: int):
    current_process().name = f"worker-{port}"
    logger.info(f"Starting server on http://0.0.0.0:{port}")
    server = HTTPServer(("0.0.0.0", port), HTTPHandler)
    server.serve_forever()


def run(workers: int = 1, start_port: int = 8000):
    for i in range(workers):
        port = start_port + i
        p = Process(target=run_server_on_port, args=(port,))
        p.start()
        logger.info(f"Worker {i + 1} started on port {port}")


if __name__ == '__main__':
    run(workers=config.WEB_SERVER_WORKERS, start_port=config.WEB_SERVER_START_PORT)