
from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from datetime import datetime, timedelta
import sqlite3
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from loader import bot
import pytz

from aiogram.types import FSInputFile

from config import CHANNEL_USERNAME, ADMIN_USERNAME
from config import ADMIN_STARS_GROUP
smWithdrawStarsRouter = Router()

@smWithdrawStarsRouter.callback_query(F.data.startswith('startmess-withdrawstars'))
async def withdraw_stars_query(query: CallbackQuery):
    build = InlineKeyboardBuilder()

    build.button(text='5⭐️ (50 звёздочек)', callback_data='changestars-5')
    build.button(text='10⭐️ (100 звёздочек)', callback_data='changestars-10')

    build.button(text='💝 (15 звёзд)', callback_data='withdrawstars-15-heart')
    build.button(text='🧸 (15 звёзд)', callback_data='withdrawstars-15-teddy')
    build.button(text='🎁 (25 звёзд)', callback_data='withdrawstars-25-gift')
    build.button(text='🌹 (25 звёзд)', callback_data='withdrawstars-25-rose')
    build.button(text='🎂 (50 звёзд)', callback_data='withdrawstars-50-cake')
    build.button(text='💐 (50 звёзд)', callback_data='withdrawstars-50-flowers')
    build.button(text='🍾 (50 звёзд)', callback_data='withdrawstars-50-bottle')
    build.button(text='🚀 (50 звёзд)', callback_data='withdrawstars-50-rocket')
    build.button(text='🏆 (100 звёзд)', callback_data='withdrawstars-100-trophy')
    build.button(text='💍 (100 звёзд)', callback_data='withdrawstars-100-ring')
    build.button(text='💎 (100 звёзд)', callback_data='withdrawstars-100-gem')
    build.button(text='назад в меню', callback_data='back_to_start_menu')
    build.adjust(2)
    withdraw_gifts = build.as_markup()

    with sqlite3.connect("database.db") as database:
        cursor = database.cursor()

        cursor.execute("SELECT balance, stars FROM users WHERE id = ?", (query.from_user.id,))
        user_data = cursor.fetchall()[0]

        cursor.execute("SELECT count FROM starsbank")
        starsbank = cursor.fetchone()[0]

    text = f'''
Казна бота: {starsbank} ⭐️

Ваш баланс:
--- {user_data[1]} ⭐️
--- {user_data[0]} ✨ (~{int(user_data[0]/10)} звёзд)

<i>Казна общая у всех пользователей. Она отображает сумму звёзд, на которую можно обменять звёздочки. Как только один из пользователей совершит обмен, баланс казны соответсвенно уменьшиться</i>
'''
    
    await bot.edit_message_text(chat_id=query.message.chat.id, message_id=query.message.message_id, text=text, parse_mode=ParseMode.HTML, reply_markup=withdraw_gifts)

    

@smWithdrawStarsRouter.callback_query(F.data.startswith('changestars'))
async def changestars_query(query: CallbackQuery):
    text, count = str(query.data).split("-")
    count = int(count)

    with sqlite3.connect("database.db") as database:
        cursor = database.cursor()

        cursor.execute("SELECT balance, stars FROM users WHERE id = ?", (query.from_user.id,))
        user_data = cursor.fetchall()[0]

        cursor.execute("SELECT count FROM starsbank")
        starsbank = cursor.fetchone()[0]

        if user_data[0] < count * 10:
            error_text = f"Недостаточно звёздочек! ({user_data[0]}/{count*10})"
            await bot.edit_message_text(text=error_text, chat_id=query.message.chat.id, message_id=query.message.message_id)
            return
        elif starsbank < count:
            error_text = f"В казне бота недостаточно звёзд! ({starsbank}/{count})"
            await bot.edit_message_text(text=error_text, chat_id=query.message.chat.id, message_id=query.message.message_id)
            return
        
        cursor.execute("UPDATE starsbank SET count = ?", (starsbank-count,))
        cursor.execute("UPDATE users SET stars = ? WHERE id = ?", (user_data[1] + count, query.from_user.id))
        cursor.execute("UPDATE users SET balance = ? WHERE id = ?", (user_data[0] - count * 10, query.from_user.id))
        await query.answer("Успешно!")


        


@smWithdrawStarsRouter.callback_query(F.data.startswith('withdrawstars'))
async def changestars_query(query: CallbackQuery):
    text, count, type = str(query.data).split("-")

    if type == "heart":
        emoji = "💝"
    elif type == "teddy":
        emoji = "🧸"
    elif type == "gift":
        emoji = "🎁"
    elif type == "rose":
        emoji = "🌹"
    elif type == "cake":
        emoji = "🎂"
    elif type == "flowers":
        emoji = "💐"
    elif type == "bottle":
        emoji = "🍾"
    elif type == "rocket":
        emoji = "🚀"
    elif type == "trophy":
        emoji = "🏆"
    elif type == "ring":
        emoji = "💍"
    elif type == "gem":
        emoji = "💎"
    else:
        await bot.send_message(chat_id=query.message.chat.id, text="ERROR!!! Некорректный гифт")
        return

    count = int(count)
    with sqlite3.connect("database.db") as database:
        cursor = database.cursor()

        cursor.execute("SELECT balance, stars FROM users WHERE id = ?", (query.from_user.id,))
        user_data = cursor.fetchall()[0]


        if user_data[1] < count:
            error_text = f"Недостаточно звёзд! ({user_data[1]}/{count})"
            await bot.edit_message_text(text=error_text, chat_id=query.message.chat.id, message_id=query.message.message_id)
            return
        
        if not query.from_user.username:
            error_text = f"Пожалуйста, установите себе username (имя пользователя) в настройках профиля telegram!"
            await bot.edit_message_text(text=error_text, chat_id=query.message.chat.id, message_id=query.message.message_id)
            return
        
        await bot.send_message(chat_id=query.message.chat.id, text=f"Заявка на вывод успешно отправлена! Пожалуйста, не изменяйте свой @username! Звёзды будут отправлены: @{query.from_user.username}. Если вы измените своё имя пользователя, то звёзды вам не придут!")
        cursor.execute("INSERT INTO transactions (id, type, amount) VALUES (?, ?, ?)", (query.from_user.id, "withdraw", count*10))
        cursor.execute("UPDATE users SET stars = ? WHERE id = ?", (user_data[1] - count, query.from_user.id))
        database.commit
    
    admin_group_text = f'''
Запросил звёзды: @{query.from_user.username}
ID: {query.from_user.id}

Сумма: {count} ⭐️
Подарок: {type} ({emoji})
'''
    build = InlineKeyboardBuilder()

    build.button(text='Подарок отправлен!', callback_data=f'admwithdraw-commit-{query.from_user.id}-{count}')
    build.button(text='Вернуть средства', callback_data=f'admwithdraw-cancel-{query.from_user.id}-{count}')

    build.adjust(2)

    admin_group_markup = build.as_markup()

    await bot.send_message(chat_id=ADMIN_STARS_GROUP, text=admin_group_text, reply_markup=admin_group_markup)


