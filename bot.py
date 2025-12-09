import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# ВСТАВЬ СВОЙ РЕАЛЬНЫЙ ТОКЕН СЮДА !!!
BOT_TOKEN = "8559685531:AAFaR0iLEZtBDCu6qSPlla_LANLJmCK5awk"

# Пароль для входа в админку
ADMIN_PASSWORD = "1234"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Бот работает!")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
