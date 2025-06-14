
from aiogram import Router, F, types
from aiogram.types import Message
from aiogram.filters import Command

from datetime import datetime, timedelta
import sqlite3
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

import pytz

from aiogram.types import FSInputFile


profileRouter = Router()


@profileRouter.message(Command('profile'))
async def profile_command(message: Message):
    user_id = message.from_user.id

    with sqlite3.connect('database.db') as database:
        cursor = database.cursor()

        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user_data = cursor.fetchone()

        if not user_data:
            await message.answer(message.chat.id, 'Для начала зарегистрируйтесь в боте: /start')
            return

        cursor.execute('SELECT prize FROM giveaways WHERE added_by_id = ?', (user_id,))
        all_added_gifts = len(cursor.fetchall())

        cursor.execute('SELECT user_id FROM invites WHERE inviter_id = ?', (user_id,))
        all_inv_friends = len(cursor.fetchall())

        today_date = datetime.now(pytz.timezone('Europe/Moscow')).strftime('%Y-%m-%d')

        cursor.execute('SELECT * FROM giveaways WHERE added_by_id = ? AND added_date = ?', (user_id, today_date))
        today_givs = len(cursor.fetchall())

        cursor.execute('SELECT * FROM invites WHERE inviter_id = ? AND invite_date = ?', (user_id, today_date))
        today_refs = len(cursor.fetchall())

        profile_text = f'''
<b>———  Ваш профиль ———</b>
➖➖➖➖➖➖➖➖➖
🔑 Ваш ID: <code>{user_data[0]}</code>
🪙 <b>Звёздочек:</b> {user_data[3]} ✨
💰 <b>Звёзд: </b>{user_data[4]} ⭐️
➖➖➖➖➖➖➖➖➖
<b> Вы добавили розыгрышей:</b>
✦ всего: {all_added_gifts} шт.
✦ сегодня: {today_givs} шт.

<b> Вы пригласили друзей:</b>
✦ всего: {all_inv_friends} шт.
✦ сегодня: {today_refs} шт.
'''
        build = InlineKeyboardBuilder()
        build.button(text='Промокод', callback_data='activate_promocode')
        build.adjust(1)
        profile_markup = build.as_markup()

        await message.answer(
                        text=profile_text,
                        parse_mode=ParseMode.HTML,
                        reply_markup=profile_markup)

