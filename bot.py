import os
import json
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

BOT_TOKEN = os.getenv("8559685531:AAFaR0iLEZtBDCu6qSPlla_LANLJmCK5awk")
ADMIN_ID = int(os.getenv("@Vachikkk_bot", "0"))  # ID админа из переменных окружения

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

GIFTS_FILE = "gifts.json"


# ------------------ Работа с файлами ------------------
def load_gifts():
    if not os.path.exists(GIFTS_FILE):
        return []
    with open(GIFTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_gifts(gifts):
    with open(GIFTS_FILE, "w", encoding="utf-8") as f:
        json.dump(gifts, f, ensure_ascii=False, indent=2)


# ------------------ Команда /start ------------------
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🎁 Список подарков", callback_data="show_gifts"))

    if message.from_user.id == ADMIN_ID:
        keyboard.add(InlineKeyboardButton("⚙️ Админка", callback_data="admin_panel"))

    await message.answer("Добро пожаловать! 👋", reply_markup=keyboard)


# ------------------ Показ подарков ------------------
@dp.callback_query_handler(lambda c: c.data == "show_gifts")
async def show_gifts(call: types.CallbackQuery):
    gifts = load_gifts()

    if not gifts:
        await call.message.answer("🎁 Список подарков пуст.")
        return

    text = "🎁 *Список подарков:*\n\n"
    text += "\n".join(f"• {g}" for g in gifts)

    await call.message.answer(text, parse_mode="Markdown")


# ------------------ Админка ------------------
@dp.callback_query_handler(lambda c: c.data == "admin_panel")
async def admin_panel(call: types.CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        return

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("➕ Добавить подарок", callback_data="add_gift"))
    keyboard.add(InlineKeyboardButton("➖ Удалить подарок", callback_data="remove_gift"))
    keyboard.add(InlineKeyboardButton("📄 Показать подарки", callback_data="show_gifts"))

    await call.message.answer("⚙️ Админ-панель", reply_markup=keyboard)


# ------------------ Добавление подарка ------------------
@dp.callback_query_handler(lambda c: c.data == "add_gift")
async def add_gift_start(call: types.CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        return
    await call.message.answer("Введите название подарка:")
    dp.register_message_handler(add_gift_finish, state=None)


async def add_gift_finish(message: types.Message):
    gift = message.text.strip()
    gifts = load_gifts()
    gifts.append(gift)
    save_gifts(gifts)

    await message.answer(f"🎉 Подарок добавлен:\n{gift}")
    dp.message_handlers.unregister(add_gift_finish)


# ------------------ Удаление подарка ------------------
@dp.callback_query_handler(lambda c: c.data == "remove_gift")
async def remove_gift_start(call: types.CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        return

    gifts = load_gifts()
    if not gifts:
        await call.message.answer("Список пуст.")
        return

    keyboard = InlineKeyboardMarkup()
    for g in gifts:
        keyboard.add(InlineKeyboardButton(f"Удалить «{g}»", callback_data=f"del_{g}"))

    await call.message.answer("Выберите подарок для удаления:", reply_markup=keyboard)


@dp.callback_query_handler(lambda c: c.data.startswith("del_"))
async def remove_gift_finish(call: types.CallbackQuery):
    gift = call.data.replace("del_", "")
    gifts = load_gifts()
    gifts = [g for g in gifts if g != gift]
    save_gifts(gifts)

    await call.message.answer(f"❌ Подарок удалён:\n{gift}")


# ------------------ Запуск ------------------
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
