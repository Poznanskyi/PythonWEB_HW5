import platform
import sys
import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timedelta


def url_by_date(date):
    logging.info("Creating URL")
    day, month, year = date.strftime("%d %m %Y").split()
    return f"https://api.privatbank.ua/p24api/exchange_rates?json&date={day}.{month}.{year}"


async def get_exchange(days=None):
    logging.info("Start exchange function")
    currency_list = ["USD", "EUR"]
    if days > 10:
        days = 10
    urls = [
        url_by_date(datetime.now() - timedelta(days=day))
        for day in range(days - 1, -1, -1)
    ]
    result_list = []
    async with aiohttp.ClientSession() as session:
        for url in urls:
            exc_for_a_date = {}
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        result = await response.json()
                        currency = {}
                        for record in result["exchangeRate"]:
                            if record["currency"] in currency_list:
                                currency[record["currency"]] = {
                                    "Sale": record["saleRate"],
                                    "Purchase": record["purchaseRate"],
                                }
                            exc_for_a_date[result["date"]] = currency
                        result_list.append(exc_for_a_date)
                        logging.info("Updating list")
                    else:
                        print(f"Error status {response.status} for {url}")
            except aiohttp.ClientConnectionError as err:
                print(f"Connection error: {url}", str(err))
        file = json.dumps(result_list, ensure_ascii=False, indent=4)
        logging.info("Creating result")
        return file


if __name__ == "__main__":
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    logging.basicConfig(level=logging.DEBUG,
                        format="%(threadName)s %(message)s")
    try:
        n = int(sys.argv[1])
    except IndexError:
        n = 1
    r = asyncio.run(get_exchange(n))
    print(r)
