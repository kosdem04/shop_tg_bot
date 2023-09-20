import asyncio
import logging

from aiogram import Bot, Dispatcher
from app.handlers import router
from app.admin import admin
from app.database.models import db_main

from config import TOKEN

bot = Bot(token=TOKEN, parse_mode="HTML")

dp = Dispatcher()

async def main():
    await db_main()

    dp.include_routers(router, admin)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот остановлен')
