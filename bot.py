import os
import json
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
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

# ------------------ Клавиатуры ------------------
def back_keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("⬅️ Назад", callback_data="admin_panel"))
    return kb

def clear_chat_keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🧹 Очистить чат", callback_data="clear_chat"))
    kb.add(InlineKeyboardButton("⬅️ Назад", callback_data="admin_panel"))
    return kb

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

    text = "<b>🎁 Список подарков:</b>\n\n"
    for idx, gift in enumerate(gifts, start=1):
        taken_mark = " ✔️ (куплено)" if gift.get("taken") else ""
        text += f"{idx}. <b>{gift['name']}</b>{taken_mark}\n"
        text += f"🔗 <a href=\"{gift['url']}\">Открыть ссылку</a>\n\n"

    await call.message.answer(text)

# ------------------ Админка ------------------
@dp.callback_query_handler(lambda c: c.data == "admin_panel")
async def admin_panel(call: types.CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        return

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("➕ Добавить подарок", callback_data="add_gift"))
    keyboard.add(InlineKeyboardButton("✏️ Редактировать", callback_data="edit_gift"))
    keyboard.add(InlineKeyboardButton("🛒 Куплено / Не куплено", callback_data="toggle_buy"))
    keyboard.add(InlineKeyboardButton("➖ Удалить подарок", callback_data="remove_gift"))
    keyboard.add(InlineKeyboardButton("📄 Показать подарки", callback_data="show_gifts"))
    keyboard.add(InlineKeyboardButton("🧹 Очистить чат", callback_data="clear_chat"))

    await call.message.answer("⚙️ Админ-панель", reply_markup=keyboard)

# ------------------ Добавление подарка ------------------
@dp.callback_query_handler(lambda c: c.data == "add_gift")
async def add_gift_start(call: types.CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        return

    await call.message.answer(
        "Введите подарок в формате:\n\n<b>Название | https://ссылка</b>",
        reply_markup=back_keyboard()
    )
    dp.register_message_handler(add_gift_finish, state=None)

async def add_gift_finish(message: types.Message):
    text = message.text.strip()
    if "|" not in text:
        return await message.answer("❌ Неверный формат.\nПример: Наушники | https://...")

    name, url = [x.strip() for x in text.split("|", 1)]
    gifts = load_gifts()
    gifts.append({"name": name, "url": url, "taken": False})
    save_gifts(gifts)

    await message.answer(f"🎉 Подарок добавлен:\n<b>{name}</b>\n🔗 {url}")
    dp.message_handlers.unregister(add_gift_finish)

# ------------------ Удаление подарка ------------------
@dp.callback_query_handler(lambda c: c.data == "remove_gift")
async def remove_gift_start(call: types.CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        return

    gifts = load_gifts()
    if not gifts:
        return await call.message.answer("❗ Список пуст.")

    keyboard = InlineKeyboardMarkup()
    for idx, gift in enumerate(gifts):
        keyboard.add(
            InlineKeyboardButton(f"Удалить «{gift['name']}»", callback_data=f"del_{idx}")
        )
    keyboard.add(InlineKeyboardButton("⬅️ Назад", callback_data="admin_panel"))
    await call.message.answer("Выберите подарок для удаления:", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data.startswith("del_"))
async def remove_gift_finish(call: types.CallbackQuery):
    idx = int(call.data.replace("del_", ""))
    gifts = load_gifts()
    if idx >= len(gifts):
        return await call.message.answer("❌ Ошибка: подарок не найден.")

    removed = gifts.pop(idx)
    save_gifts(gifts)
    await call.message.answer(f"🗑 Подарок удалён:\n<b>{removed['name']}</b>")

# ------------------ Отметить как купленный ------------------
@dp.callback_query_handler(lambda c: c.data == "toggle_buy")
async def toggle_buy_list(call: types.CallbackQuery):
    gifts = load_gifts()
    if not gifts:
        return await call.message.answer("Список пуст.")

    kb = InlineKeyboardMarkup()
    for idx, g in enumerate(gifts):
        mark = "✔️" if g.get("taken") else "❌"
        kb.add(InlineKeyboardButton(f"{mark} {g['name']}", callback_data=f"buy_{idx}"))
    kb.add(InlineKeyboardButton("⬅️ Назад", callback_data="admin_panel"))
    await call.message.answer("Выберите подарок:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith("buy_"))
async def toggle_buy_finish(call: types.CallbackQuery):
    idx = int(call.data.replace("buy_", ""))
    gifts = load_gifts()
    gifts[idx]["taken"] = not gifts[idx].get("taken")
    save_gifts(gifts)

    state = "куплен" if gifts[idx]["taken"] else "не куплен"
    await call.message.answer(f"🛒 Статус обновлён: <b>{gifts[idx]['name']}</b> — {state}")

# ------------------ Редактирование подарка ------------------
edit_memory = {}  # временное хранилище

@dp.callback_query_handler(lambda c: c.data == "edit_gift")
async def edit_choose(call: types.CallbackQuery):
    gifts = load_gifts()
    kb = InlineKeyboardMarkup()
    for idx, g in enumerate(gifts):
        kb.add(InlineKeyboardButton(g["name"], callback_data=f"edit_{idx}"))
    kb.add(InlineKeyboardButton("⬅️ Назад", callback_data="admin_panel"))
    await call.message.answer("Выберите подарок для редактирования:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith("edit_"))
async def edit_start(call: types.CallbackQuery):
    idx = int(call.data.replace("edit_", ""))
    edit_memory[call.from_user.id] = idx
    await call.message.answer(
        "Введите новый формат:\n<b>Название | ссылка</b>",
        reply_markup=back_keyboard()
    )
    dp.register_message_handler(edit_finish, state=None)

async def edit_finish(message: types.Message):
    idx = edit_memory.get(message.from_user.id)
    if idx is None:
        return

    text = message.text.strip()
    if "|" not in text:
        return await message.answer("❌ Неверный формат.")

    name, url = [x.strip() for x in text.split("|", 1)]
    gifts = load_gifts()
    gifts[idx]["name"] = name
    gifts[idx]["url"] = url
    save_gifts(gifts)

    await message.answer("✏️ Подарок обновлён!")
    dp.message_handlers.unregister(edit_finish)
    del edit_memory[message.from_user.id]

# ------------------ Очистка чата ------------------
@dp.callback_query_handler(lambda c: c.data == "clear_chat")
async def clear_chat(call: types.CallbackQuery):
    user_id = call.from_user.id
    chat_id = call.message.chat.id

    if user_id == ADMIN_ID:
        try:
            # Получаем последние 50 сообщений (бот должен быть админом с правом delete_messages)
            messages = await call.message.chat.get_history(limit=50)
            deleted_count = 0
            for msg in messages:
                try:
                    await bot.delete_message(chat_id, msg.message_id)
                    deleted_count += 1
                except:
                    continue
            await call.message.answer(f"🧹 Админ: удалено {deleted_count} сообщений.")
        except Exception as e:
            await call.message.answer(f"❌ Не удалось удалить сообщения: {e}")
    else:
        # Обычный пользователь удаляет только своё сообщение
        try:
            await bot.delete_message(chat_id, call.message.message_id)
            await call.message.answer("🧹 Ваше сообщение удалено.")
        except Exception as e:
            await call.message.answer(f"❌ Не удалось удалить сообщение: {e}")

# ------------------ Запуск ------------------
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
