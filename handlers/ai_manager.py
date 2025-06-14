from aiogram import types, F, Router
from aiogram.types import ContentType
import asyncio
import sqlite3
from concurrent.futures import ThreadPoolExecutor

from openai import OpenAI  # Заменили библиотеку
from config import TOKEN, AI_RULES_GROUP, AI_RULES_DM, OPENROUTER_API_KEY  # Используем тот же ключ
from loader import bot
import pytz
from datetime import datetime, timedelta
differentTextRouter = Router()
requestRouter = Router()
executor = ThreadPoolExecutor()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)


def add_to_history(chat_history, role, text):
    chat_history.append({"role": role, "content": text})  # Формат под OpenRouter


# Фоновая функция: отправка "печатает..."
async def show_typing(chat_id: int):
    try:
        while True:
            await bot.send_chat_action(chat_id=chat_id, action="typing")
            await asyncio.sleep(4)
    except asyncio.CancelledError:
        pass


# Основная логика ответа от ИИ
async def AI_assistant(bot_message: types.Message, AI_RULES: str):
    typing_task = asyncio.create_task(show_typing(bot_message.chat.id))

    try:
        with sqlite3.connect('database.db') as database:
            cursor = database.cursor()
            cursor.execute('SELECT role, text FROM requests WHERE id = ?', (bot_message.from_user.id,))
            user_requests = cursor.fetchall()
            cursor.close()

        chat_history = []
        if user_requests:
            for request in user_requests:
                add_to_history(chat_history, request[0], request[1])

        add_to_history(chat_history, "user", AI_RULES)
        add_to_history(chat_history, "user", bot_message.text)

        loop = asyncio.get_running_loop()
        completion = await loop.run_in_executor(
            executor,
            lambda: client.chat.completions.create(
                model="qwen/qwen3-30b-a3b:free",
                messages=chat_history,
                extra_body={}
            )
        )

        try:
            answer = completion.choices[0].message.content
        except (IndexError, AttributeError):
            answer = "Извините, произошла ошибка при обработке запроса."

        if "False" in answer:
            answer = None

        now_date = datetime.now(pytz.timezone('Europe/Moscow')).strftime('%Y-%m-%d')
        yest_date = (datetime.now(pytz.timezone('Europe/Moscow')) - timedelta(days=1)).strftime('%Y-%m-%d')
        if answer:
            with sqlite3.connect('database.db') as database:
                cursor = database.cursor()
                cursor.execute("DELETE FROM requests WHERE date < ?", (yest_date,))
                database.commit()
                cursor.execute('INSERT INTO requests (id, role, text, date) VALUES (?, ?, ?, ?)',
                           (bot_message.from_user.id, "user", bot_message.text, now_date))
                database.commit()
                cursor.execute('INSERT INTO requests (id, role, text, date) VALUES (?, ?, ?, ?)',
                           (bot_message.from_user.id, "assistant", answer, now_date))
                database.commit()
                cursor.close()

    finally:
        typing_task.cancel()

    return answer


@differentTextRouter.message(F.content_type == ContentType.TEXT)
async def message_handler(message: types.Message):
    if message.from_user.id != message.chat.id:
        result = await AI_assistant(message, AI_RULES_GROUP)
    else:
        result = await AI_assistant(message, AI_RULES_DM)

    if result:
        if not "False" in result:
            await message.reply(result, parse_mode="HTML")
