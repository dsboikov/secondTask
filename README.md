# Учебный проект "Хостинг изображений"

## Описание
Учебный проект, реализующий функционал простейшего хранилища изображений, использующий Python в качестве бэкенда и стек html-js-css для фронтэнда. За маршрутизацию отвечает nginx.

## Функционал приложения
Приложение позволяет загружать изображения формата `.jpg`, `.jpeg`, `.png`, `.gif`, просматривать и получать ссылки на них.

## Структура проекта
- Директория "app" содержит серверную логику приложения
- Директория "images" создано для хранения изображений 
- Директория "logs" создано для хранения логов приложения 
- Директория "static" содержит скрипты js, изображения, стили и html-файлы

## Маршруты API
- `/api/images/` - получение списка изображений методом `GET`
- `/api/upload/` - загрузка изображений методом `POST`
- `/api/delete/` - удаление изображения методом `DELETE`

## Требования к окружению
- Установлен Docker 
- Установлен Docker-compose 
- Установлен git (если используется git)

## Установка
- клонировать репозиторий или скачать и разархивировать архив на сервер/локальный компьютер
- перейти в директорию с файлами проекта (по умолчанию `secondTask`)
- запустить с помощью команды:
  ```bash
  docker compose up --build
  ```
- открыть браузер и перейти по ссылке http://<ваш ip адрес>/
