# Используем официальный образ Python
FROM python:3.10-slim

# Устанавливаем зависимости для PostgreSQL
RUN apt-get update && apt-get install -y \
    libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл requirements.txt из корневой директории в контейнер
COPY ./requirements.txt /app/

# Устанавливаем зависимости из requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы проекта (папку app) в контейнер
COPY . /app

# Команда для запуска приложения
CMD ["python", "main.py"]

