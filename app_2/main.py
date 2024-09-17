import asyncio
from scraper import scrape_all_marketplaces
from database import init_db
from tortoise import Tortoise


# Основная функция для запуска приложения
async def main():
    # Инициализация базы данных
    await init_db()

    # Запуск парсинга маркетплейсов
    await scrape_all_marketplaces()

    # Закрытие соединения с базой данных
    await Tortoise.close_connections()


if __name__ == "__main__":
    # Запуск основного приложения
    asyncio.run(main())
