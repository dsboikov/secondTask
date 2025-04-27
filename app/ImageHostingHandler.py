import os
import logging
from advanced_http_request_handler import AdvancedHTTPRequestHandler
from db_client import PostgresClient
from settings import IMAGES_PATH, ALLOWED_EXTENSIONS, MAX_FILE_SIZE
from uuid import uuid4


class ImageHostingHttpRequestHandler(AdvancedHTTPRequestHandler):
    server_version = 'Image Hosting Server v0.2'

    def get_images_count(self) -> None:
        with PostgresClient() as db:
            count = db.get_total_images()

        logging.info('Count: ' + str(count))
        self.send_json({
            'count': count
        })

    def get_images(self) -> None:
        page = self.headers.get('Page') or 1
        limit = self.headers.get('Limit') or 10
        logging.info(f'Page: {page}, Limit: {limit}')
        with PostgresClient() as db:
            images = db.get_images(int(page), int(limit))

        if not images:
            return self.send_json({'images': []})

        json_images = []
        for image in images:
            json_images.append({
                'filename': image['filename'],
                'original_name': image['original_name'],
                'size': image['size'],
                'upload_time': image['upload_time'].strftime('%Y-%m-%d %H:%M:%s'),
                'file_type': image['file_type']
            })
        return self.send_json({
            'images': json_images
        })

    def upload_image(self) -> None:
        length = int(self.headers.get('Content-Length'))
        if length > MAX_FILE_SIZE:
            logging.warning('File too large')
            return self.send_json({'error': 'File too large', 'code': 413})

        data = self.rfile.read(length)
        orig_filename = self.headers.get('Filename')
        _, ext = os.path.splitext(orig_filename)
        image_id = str(uuid4())
        if ext not in ALLOWED_EXTENSIONS:
            logging.warning('File type not allowed')
            return self.send_json({'error': 'File type not allowed', 'code': 415})

        with PostgresClient() as db:
            db.add_image(orig_filename, image_id, length, ext)

        with open(IMAGES_PATH + f'{image_id}{ext}', 'wb') as file:
            file.write(data)
        return self.send_json({'success': f'Image uploaded as {image_id}{ext}',
                        'location': f'http://localhost/{IMAGES_PATH}{image_id}{ext}'})

    def delete_image(self, image_id) -> None:
        if not image_id:
            logging.warning('No filename provided')
            return self.send_json({'error': 'File not found', 'code': 404})

        image_path = IMAGES_PATH + image_id
        if not os.path.exists(image_path):
            logging.warning(f'Image not found {image_path}')
            return self.send_json({'error': 'File not found', 'code': 404})

        filename, _ = os.path.splitext(image_id)

        with PostgresClient() as db:
            file_id = db.get_image_by_filename(filename)

        if not file_id:
            logging.warning(f'Image not found {filename}')
            return self.send_json({'error': 'File not found', 'code': 404})

        os.remove(image_path)
        with PostgresClient() as db:
            db.delete_image(file_id['id'])

        return self.send_json({'Success': 'Image deleted'})
