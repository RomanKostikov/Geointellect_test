import aiohttp
import asyncio

# Базовые URL для бирж с поддержкой динамической вставки символов пар
BASE_URLS = {
    "binance": "https://api.binance.com/api/v3/ticker/price?symbol={pair}",
    "gateio": "https://api.gateio.ws/api/v4/spot/tickers?currency_pair={pair}",
    "kucoin": "https://api.kucoin.com/api/v1/market/orderbook/level1?symbol={pair}"
}

# Преобразование пар в формат для каждой биржи
PAIR_CONVERSIONS = {
    "binance": lambda pair: pair.replace("/", ""),
    "gateio": lambda pair: pair.replace("/", "_"),
    "kucoin": lambda pair: pair.replace("/", "-")
}

# Поддерживаемые пары для каждой биржи
SUPPORTED_PAIRS = {
    "binance": ["BTC/USDT", "BTC/RUB"],  # Binance не поддерживает другие пары
    "gateio": ["BTC/USDT"],  # Gate.io поддерживает только USDT в данном запросе
    "kucoin": ["BTC/USDT"]  # KuCoin также имеет ограничения по поддержке
}


# Асинхронный запрос к API бирж
async def fetch_price(url):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    print(f"Ошибка при запросе {url}: статус {response.status}")
                    return None
                return await response.json()
        except Exception as e:
            print(f"Ошибка при обработке {url}: {e}")
            return None


# Получаем цены для всех бирж и всех пар
async def get_prices():
    prices = {}

    for exchange, base_url in BASE_URLS.items():
        for pair in SUPPORTED_PAIRS[exchange]:
            # Формируем символ пары для конкретной биржи
            formatted_pair = PAIR_CONVERSIONS[exchange](pair)

            # Создаем URL для запроса
            url = base_url.format(pair=formatted_pair)

            # Получаем данные с биржи
            price_data = await fetch_price(url)

            if price_data:
                # Вывод для проверки структуры данных
                print(f"Данные от {exchange} для пары {pair}: {price_data}")

                # Обрабатываем ответ для каждой биржи
                if exchange == "binance":
                    if 'symbol' in price_data and 'price' in price_data:
                        prices[f"{exchange}-{pair}"] = {
                            'symbol': price_data['symbol'],
                            'price': price_data['price']
                        }
                    else:
                        print(
                            f"Ошибка данных от Binance для пары {pair}: {price_data.get('msg', 'Нет символа или цены')}")

                elif exchange == "gateio":
                    if isinstance(price_data, list) and len(price_data) > 0 and 'last' in \
                            price_data[0]:
                        prices[f"{exchange}-{pair}"] = {
                            'symbol': pair,
                            'price': price_data[0]['last']
                        }
                    else:
                        print(f"Ошибка данных от Gate.io для пары {pair}: {price_data}")

                elif exchange == "kucoin":
                    if price_data.get('data') is not None and 'price' in price_data['data']:
                        prices[f"{exchange}-{pair}"] = {
                            'symbol': pair,
                            'price': price_data['data']['price']
                        }
                    else:
                        print(
                            f"Ошибка данных от KuCoin для пары {pair}: {price_data.get('msg', 'Нет данных')}")
            else:
                print(f"Не удалось получить данные от {exchange} для пары {pair}")

    return prices


# Для теста
async def main():
    prices = await get_prices()
    print(prices)


# Запуск для тестирования
if __name__ == "__main__":
    asyncio.run(main())
