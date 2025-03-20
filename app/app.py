from http.server import HTTPServer
import logging
from ImageHostingHandler import ImageHostingHttpRequestHandler
from settings import SERVER_ADDRESS, LOG_PATH, LOG_FILE

# Настройка логирования
logging.basicConfig(
    filename = LOG_PATH + LOG_FILE,
    level = logging.INFO,
    format = "[%(asctime)s] - %(levelname)s - %(message)s"
)

def run(server_class=HTTPServer, handler_class=ImageHostingHttpRequestHandler):
    httpd = server_class(SERVER_ADDRESS, handler_class)
    logging.info(f'Serving on http://{SERVER_ADDRESS[0]}:{SERVER_ADDRESS[1]}')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logging.warning('Keyboard interrupt received, exiting.')
        httpd.server_close()
    finally:
        logging.info('Server stopped.')


if __name__ == '__main__':
    run()
