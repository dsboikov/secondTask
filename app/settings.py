import os
from dotenv import load_dotenv

load_dotenv()

SERVER_ADDRESS = (os.getenv('SERVER_ADDRESS').split(':')[0], int(os.getenv('SERVER_ADDRESS').split(':')[1]))
STATIC_PATH = os.getenv('STATIC_PATH')
IMAGES_PATH = os.getenv('IMAGES_PATH')
ALLOWED_EXTENSIONS = os.getenv('ALLOWED_EXTENSIONS').split(',')
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE'))
LOG_PATH = os.getenv('LOG_PATH')
LOG_FILE = os.getenv('LOG_FILE')
ERROR_FILE = os.getenv('ERROR_FILE')
PAGE_LIMIT = os.getenv('PAGE_LIMIT')
