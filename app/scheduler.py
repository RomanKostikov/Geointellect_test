import schedule
import asyncio
from fetcher import get_prices
from database import save_to_db, get_previous_price
from notifications import send_email

# Количество BTC, накопленных Лакрицей
BTC_HOLDINGS = 3


# Функция для проверки цен и вычисления разницы
async def check_prices():
    # Получаем текущие цены с бирж
    prices = await get_prices()

    for exchange, price_data in prices.items():
        print(f"Полученные данные от {exchange}: {price_data}")

        # Извлекаем символ валютной пары
        pair = price_data.get('symbol')

        # Получаем предыдущую цену для данной биржи и валютной пары
        previous_price = await get_previous_price(exchange, pair)

        # Считаем стоимость накоплений Лакрицы (3 BTC)
        current_price = float(price_data['price'])
        current_value = BTC_HOLDINGS * current_price

        # Если предыдущая цена существует, вычисляем разницу
        if previous_price:
            previous_value = BTC_HOLDINGS * previous_price
            difference = ((
                                  current_value - previous_value) / previous_value) * 100  # Разница в процентах
            print(f"Разница для {pair} на {exchange}: {difference:.2f}%")
            print(f"Стоимость накоплений: {current_value:.2f}")

            # Проверка на наличие символа '/' в паре валют
            if '/' in pair:
                currency = pair.split('/')[1]
            else:
                currency = 'В валюте данной пары'  # Установить значение по умолчанию или обработать случай

            # Отправляем email, если разница превышает 0.01%(для тестирования) (порог можно настроить под условие задачи)
            if abs(difference) >= 0.01:  # Порог в 0.01% по модулю
                send_email(
                    'Price Alert',
                    f"Количество накоплений Лакрицы ({BTC_HOLDINGS} BTC) на {exchange} для пары {pair} "
                    f"изменилась на {difference:.2f}%. Стоимость накоплений: {current_value:.2f} {currency}",
                    'recipient@example.com'
                )
        else:
            print(f"Предыдущая цена для {pair} на {exchange} отсутствует.")

        # Сохраняем текущую цену в базу данных вместе с предыдущей
        await save_to_db(exchange, pair, price_data, previous_price)


# Функция для запуска планировщика
async def start_scheduler():
    # Запускаем функцию check_prices каждые 1 минуту
    schedule.every(1).minutes.do(lambda: asyncio.create_task(check_prices()))

    # Асинхронный цикл для выполнения запланированных задач
    while True:
        schedule.run_pending()
        # Небольшая пауза, чтобы не перегружать процессор
        await asyncio.sleep(1)
