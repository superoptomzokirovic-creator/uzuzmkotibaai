import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers import product_handler, calculator_handler, cargo_handler

async def main():
    if not BOT_TOKEN or BOT_TOKEN == "your_telegram_bot_token_here":
        print("❌ XATOLIK: BOT_TOKEN .env faylida kiritilmagan! Iltimos, tokeningizni yozing.")
        sys.exit(1)

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Routerlarni ulash
    dp.include_router(product_handler.router)
    dp.include_router(calculator_handler.router)
    dp.include_router(cargo_handler.router)

    logging.basicConfig(level=logging.INFO)
    print("🚀 Uzum Business Bot muvaffaqiyatli ishga tushdi va xabarlarni kutmoqda...")

    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot to'xtatildi.")
