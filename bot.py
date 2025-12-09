import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

BOT_TOKEN = os.environ.get("8559685531:AAFaR0iLEZtBDCu6qSPlla_LANLJmCK5awk")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Бот работает!")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
