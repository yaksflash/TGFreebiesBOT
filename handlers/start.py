import logging
import asyncio
from aiogram import Router, F, types
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from datetime import datetime, timedelta, timezone
import sqlite3
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

import random
from config import CHANNEL_USERNAME, ADMIN_USERNAME

startRouter = Router()


def check_admin_status(user_id):
    with sqlite3.connect('database.db') as database:
        cursor = database.cursor()

        cursor.execute('SELECT status FROM users WHERE id = ?', (user_id,))
        user_status = cursor.fetchone()

        if not user_status:
            return False

        if user_status[0] == 'admin' or user_id == 929185014:
            return True
        else:
            if user_status[0] == 'manager':
                return 'manager'
            else:
                return False
            

def to_datetime(dt):
    if isinstance(dt, (int, float)):
        return datetime.fromtimestamp(dt, tz=timezone.utc)
    elif isinstance(dt, datetime):
        return dt
    else:
        raise TypeError(f"Unsupported type for date: {type(dt)}")


def registration_info(id):
    with sqlite3.connect('database.db') as database:
        cursor = database.cursor()

        cursor.execute('SELECT * FROM users WHERE id = ?', (id,))
        user_data = cursor.fetchone()

        cursor.close()

    if user_data:
        return True
    else:
        return False



@startRouter.message(CommandStart())
async def start_command(message: types.Message):
    bot = message.bot
    user_id = message.from_user.id
    time = (to_datetime(message.date) + timedelta(hours=3)).strftime('%Y-%m-%d')

    async def register_user(user_id, username, inviter_id, date):
        with sqlite3.connect('database.db') as database:
            cursor = database.cursor()

            cursor.execute('INSERT INTO users (id, name, status, balance, stars) VALUES (?, ?, ?, ?, ?)',
                            (user_id, username, 'user', 0, 0))
            database.commit()

            if inviter_id:
                cursor.execute('INSERT INTO invites (user_id, inviter_id, invite_date) VALUES (?, ?, ?)',
                            (user_id, inviter_id, date))
                database.commit()
                
                await bot.send_message(inviter_id, f'Вы пригласили друга: @{username}')

                cursor.execute('SELECT balance FROM users WHERE id = ?', (inviter_id,))
                inviter_points = cursor.fetchone()[0]

                reward = random.randint(5, 10)
                cursor.execute("INSERT INTO transactions (id, type, amount) VALUES (?, ?, ?)", (inviter_id, "invite", reward))
                cursor.execute('UPDATE users SET balance = ? WHERE id = ?', (inviter_points + reward, inviter_id))
                


    if not registration_info(user_id):
        if 'ref' in message.text:
            txt, inviter_id = message.text.split('_')

            if not registration_info(inviter_id):
                await message.answer('<b>Неверная ссылка приглашения!</b>\nВы не были зарегестрированы (попросите новую пригласительную ссылку или напишите /start)', parse_mode='html')
                return 0
            else:
                await register_user(user_id, message.from_user.username, inviter_id, time)
        else:
            await register_user(user_id, message.from_user.username, False, time)
    else:
        if 'ref' in message.text:
            await message.answer('Вы уже являетесь пользователем бота!')
            return 0
        
    
    hello_text = f'''
❶ Приглашай друзей, пересылай розыгрыши боту и получай звёздочки
❷ Накопи достаточное количество звёздочек и обменяй их на телеграм-подарки!

--- А также:
◉ Добавляй папки и участвуй в публичных розыгрышах премиумов и звёзд бесплатно
◉ Просто напиши свой вопрос, ИИ-ассистент вам подскажет!
◉ Заходи на наш канал, там часто происходят раздачи

💎 <b>Наш канал:</b> @{CHANNEL_USERNAME}
❤️ <b>Создатель:</b> @{ADMIN_USERNAME}
'''
    if check_admin_status(message.from_user.id):
        hello_text += """
\n\n\n\n<b>Бонус для админов:</b>



Оповещение пользователей:
/folder_updated_today
/folder_updated_tomorrow








Список розыгрышей:
/admin_giveaways








Управление папками:
/add_folder
/del_folder
"""

    build = InlineKeyboardBuilder()

    build.button(text='🚀 Публичные розыгрыши 🚀', callback_data='startmess-giveaways')
    build.button(text='⭐️ Заработать звёзды ⭐️', callback_data='startmess-earnstars')
    build.button(text='👤 Профиль', callback_data='startmess-profile')
    build.button(text='💰 Вывод звёзд', callback_data='startmess-withdrawstars')
    build.button(text='📗 Информация', callback_data='startmess-info')
    build.button(text='📂 Папки', callback_data='startmess-folders')
    build.button(text='💌 Отзывы', url='https://t.me/tg_freebies_reviews')

    build.adjust(1, 1, 2, 2, 1)

    start_markup = build.as_markup()

                   
    await message.answer(hello_text, parse_mode=ParseMode.HTML, reply_markup=start_markup)
