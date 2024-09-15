from scheduler import start_scheduler
from database import init_db
import asyncio
from notifications import send_email


async def main():
    # Инициализация базы данных
    await init_db()

    # Запуск системы мониторинга цен
    await start_scheduler()


if __name__ == '__main__':
    asyncio.run(main())
