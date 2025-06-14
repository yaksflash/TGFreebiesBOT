
from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from datetime import datetime, timedelta
import sqlite3
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from loader import bot
import pytz
from config import REVIEWS_CHANNEL_TAG
from aiogram.types import FSInputFile

from config import CHANNEL_USERNAME, ADMIN_USERNAME
from config import ADMIN_STARS_GROUP
admWithdrawStarsRouter = Router()

@admWithdrawStarsRouter.callback_query(F.data.startswith('admwithdraw-'))
async def withdraw_stars_query(query: CallbackQuery):
    _, status, user_id, count = query.data.split('-')
    count = int(count)
    if status == "commit":
        text = "Подарок был успешно отправлен!"

        build = InlineKeyboardBuilder()
        build.button(text='💌 Оставить отзыв (пожалуйста)', url=f'https://t.me/{REVIEWS_CHANNEL_TAG}')
        gift_markup = build.as_markup()

        await bot.send_message(chat_id=user_id, text=text, reply_markup=gift_markup)
    elif status == "cancel":
        text = f"Запрос на вывод подарка был отклонён! {count}⭐️ возвращены на баланс!"
        with sqlite3.connect("database.db") as database:
            cursor = database.cursor()

            cursor.execute("SELECT balance, stars FROM users WHERE id = ?", (query.from_user.id,))
            user_data = cursor.fetchall()[0]

            cursor.execute("UPDATE users SET stars = ? WHERE id = ?", (user_data[1] + count, user_id))
        
        await bot.send_message(chat_id=user_id, text=text)
    
    admin_group_text = f'''
Запросил звёзды: @{query.from_user.username}
ID: {query.from_user.id}

Сумма: {count} ⭐️
Статус: {status}
'''
    await bot.edit_message_text(text=admin_group_text, chat_id=query.message.chat.id, message_id=query.message.message_id, reply_markup=None)
    