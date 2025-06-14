from aiogram import types, F, Router
from aiogram.types import ContentType
import asyncio
import sqlite3
from concurrent.futures import ThreadPoolExecutor

from google import genai

from config import TOKEN, AI_RULES_GROUP, AI_RULES_DM, GEMINI_API_KEY
from loader import bot

differentTextRouter = Router()
client = genai.Client(api_key=GEMINI_API_KEY)
requestRouter = Router()
executor = ThreadPoolExecutor()


def add_to_history(chat_history, role, text):
    chat_history.append({"role": role, "parts": [{"text": text}]})


# Фоновая функция: отправка "печатает..."
async def show_typing(chat_id: int):
    try:
        while True:
            await bot.send_chat_action(chat_id=chat_id, action="typing")
            await asyncio.sleep(4)
    except asyncio.CancelledError:
        pass  # Корректно завершаем при cancel


# Основная логика ответа от ИИ
async def AI_assistant(bot_message: types.Message, AI_RULES: str):
    typing_task = asyncio.create_task(show_typing(bot_message.chat.id))

    try:
        # Загружаем историю запросов из БД
        with sqlite3.connect('database.db') as database:
            cursor = database.cursor()
            cursor.execute('SELECT role, text FROM requests WHERE id = ?', (bot_message.from_user.id,))
            user_requests = cursor.fetchall()
            cursor.close()

        chat_history = []
        if user_requests:
            for request in user_requests:
                add_to_history(chat_history, request[0], request[1])

        # Добавляем правила как обычное сообщение от пользователя
        add_to_history(chat_history, "user", AI_RULES)
        # Добавляем сообщение пользователя
        add_to_history(chat_history, "user", bot_message.text)

        
        # Генерация ответа ИИ в отдельном потоке
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(
            executor,
            lambda: client.models.generate_content(
                model="gemini-1.5-flash",
                contents=chat_history
            )
        )

        try:
            answer = response.candidates[0].content.parts[0].text
        except (IndexError, AttributeError):
            answer = "Извините, произошла ошибка при обработке запроса."

        if answer == "False":
            answer = None

        # Сохраняем в историю
        with sqlite3.connect('database.db') as database:
            cursor = database.cursor()
            cursor.execute('INSERT INTO requests (id, role, text) VALUES (?, ?, ?)',
                           (bot_message.from_user.id, "user", bot_message.text))
            database.commit()
            cursor.execute('INSERT INTO requests (id, role, text) VALUES (?, ?, ?)',
                           (bot_message.from_user.id, "assistant", answer))
            database.commit()
            cursor.close()

    finally:
        typing_task.cancel()  # Останавливаем индикацию "печатает..."

    return answer


# Обработка всех текстовых сообщений
@differentTextRouter.message(F.content_type == ContentType.TEXT)
async def message_handler(message: types.Message):
    if message.from_user.id != message.chat.id:
        result = await AI_assistant(message, AI_RULES_GROUP)
    else:
        result = await AI_assistant(message, AI_RULES_DM)

    if result:
        if not "False" in result:
            await message.answer(result, parse_mode="HTML")
