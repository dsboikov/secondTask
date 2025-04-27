from http.server import HTTPServer
import logging
from db_client import PostgresClient
from router import Router
from ImageHostingHandler import ImageHostingHttpRequestHandler
from settings import SERVER_ADDRESS, LOG_PATH, LOG_FILE

# Настройка логирования
logging.basicConfig(
    filename=LOG_PATH + LOG_FILE,
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(message)s"
)


def run(server_class=HTTPServer, handler_class=ImageHostingHttpRequestHandler):
    """ Подключаемся к базе данных """
    PostgresClient()
    """ Создаем экземпляр роутера """
    router = Router()
    """ Добавляем маршруты в роутер """
    router.add_route('GET', '/api/images/', handler_class.get_images)
    router.add_route('GET', '/api/images_count/', handler_class.get_images_count)
    router.add_route('POST', '/upload/', handler_class.upload_image)
    router.add_route('DELETE', '/api/delete/<image_id>', handler_class.delete_image)

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
