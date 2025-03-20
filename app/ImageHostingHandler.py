import os
from uuid import uuid4
import logging
from advanced_http_request_handler import AdvancedHTTPRequestHandler
from settings import IMAGES_PATH, ALLOWED_EXTENSIONS, MAX_FILE_SIZE


class ImageHostingHttpRequestHandler(AdvancedHTTPRequestHandler):
    server_version = 'Image Hosting Server v0.2'

    def __init__(self, request, client_address, server):

        self.get_routes = {
            '/images/': self.get_images
        }
        self.post_routes = {
            '/upload/': self.post_upload
        }
        self.delete_routes = {
            '/api/delete/': self.delete_image
        }
        super().__init__(request, client_address, server)

    def get_images(self):
        self.send_json({
            'images': next(os.walk(IMAGES_PATH))[2]
        })

    def post_upload(self):
        length = int(self.headers.get('Content-Length'))
        if length > MAX_FILE_SIZE:
            logging.warning('UPLOAD: File too large')
            self.send_json({'error': 'File too large', 'code': 413})
            return

        data = self.rfile.read(length)
        _, ext = os.path.splitext(self.headers.get('Filename'))
        image_id = uuid4()
        if ext not in ALLOWED_EXTENSIONS:
            logging.warning('UPLOAD: File type not allowed')
            self.send_json({'error': 'File type not allowed', 'code': 415})
            return

        file_name = f'{image_id}{ext}'
        with open(IMAGES_PATH + f'{file_name}', 'wb') as file:
            file.write(data)
        logging.info(f'UPLOAD: Image {file_name} uploaded')
        self.send_json({'success': f'Image uploaded as {file_name}',
                        'location': f'http://localhost/{IMAGES_PATH}{image_id}{ext}'})

    def delete_image(self):
        image_id = self.headers.get('Filename')
        if not image_id:
            logging.warning('DELETE: Image not found')
            self.send_json({'error': 'Image not found', 'code': '404'})
            return

        image_path = IMAGES_PATH + image_id
        if not os.path.exists(image_path):
            logging.warning('DELETE: Image not found')
            self.send_json({'error': 'Image not found', 'code': '404'})
            return

        os.remove(image_path)
        logging.info(f'DELETE: Image {image_path} deleted')
        self.send_json({'success': 'Image deleted'})
