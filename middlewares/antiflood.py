import time
from collections import defaultdict
from aiogram import types
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import TelegramObject, ContentType

# Хранилище времени последнего действия пользователя
last_action_time = defaultdict(float)

# Задержка между действиями (в секундах)
DELAY = 0.5

# Middleware антифлуда
async def antiflood_middleware(handler, event: TelegramObject, data: dict):
    user_id = event.from_user.id
    now = time.time()

    # Пропускаем антифлуд для розыгрышей
    if isinstance(event, types.Message):
        if event.content_type == ContentType.GIVEAWAY:
            return await handler(event, data)

    # Проверка задержки
    if now - last_action_time[user_id] < DELAY:
        if isinstance(event, types.CallbackQuery):
            await event.answer("Не так быстро!", show_alert=False)
        return

    # Обновляем время последнего действия
    last_action_time[user_id] = now
    return await handler(event, data)
