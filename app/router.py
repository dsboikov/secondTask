import re
import logging


class Router:
    _instance = None  # Хранение экземпляра Singleton

    def __new__(cls):
        """Реализация паттерна Singleton"""
        if cls._instance is None:
            cls._instance = super(Router, cls).__new__(cls)
            cls._instance.routes = {
                'GET': {},
                'POST': {},
                'DELETE': {},
            }
        return cls._instance

    @staticmethod
    def convert_path(path):
        """
        Преобразует путь с параметрами в регулярное выражение.
        Например: '/api/delete/<id>' -> '/api/delete/(?P<id>[^/]+)'
        """
        return re.sub(r'<(\w+)>', r'(?P<\1>[^/]+)', path)

    def add_route(self, method, path, handler):
        """
        Добавляет маршрут для указанного HTTP-метода.
        :param method: HTTP-метод (GET, POST, DELETE).
        :param path: Путь маршрута с возможными параметрами.
        :param handler: Обработчик маршрута.
        """
        if method not in self.routes:
            raise ValueError(f"Unsupported HTTP method: {method}")

        pattern = self.convert_path(path)
        compiled = re.compile(pattern)
        self.routes[method][compiled] = handler
        logging.info(f"Added route: {method} {path}")

    def resolve(self, method, path):
        """
        Разрешает маршрут для указанного HTTP-метода и пути.
        :param method: HTTP-метод (GET, POST, DELETE).
        :param path: Запрошенный путь.
        :return: Кортеж (обработчик, параметры) или (None, {}) если маршрут не найден.
        """
        logging.info(f"Resolving {method} {path}")
        if method not in self.routes:
            logging.warning(f"Unsupported HTTP method: {method}")
            return None, {}

        for pattern, handler in self.routes[method].items():
            match = pattern.match(path)
            if match:
                logging.info(f"Found handler for {method} {path}")
                kwargs = match.groupdict()
                return handler, kwargs

        logging.warning(f"No handler found for {method} {path}")
        return None, {}
