
from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from datetime import datetime, timedelta
import sqlite3
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

import pytz
from loader import bot
from aiogram.types import FSInputFile


smEarnStarsRouter = Router()

@smEarnStarsRouter.callback_query(F.data.startswith('startmess-earnstars'))
async def earn_stars_call(query: CallbackQuery):
    user_id = query.from_user.id

    user_link = f'https://t.me/tg_freebies_bot?start=ref_{user_id}'

    es_text = f'''
<b>🎉 Приглашай друзей и получай по 5-10 ✨ за каждого, кто активирует бота по твоей ссылке!</b>

<b>🔗 Твоя личная ссылка (нажми чтобы скопировать):</b>

<code>{user_link}</code>


<b>Как ещё можно получать звёзды?</b>
Пересылайте розыгрыши звёзд и премиумов боту и получите 1-3 звёздочки!


<b>10 ✨ = 1 ⭐️</b>
'''
    
    build = InlineKeyboardBuilder()
    build.button(text='Промокод', callback_data='activate_promocode')
    build.button(text='назад в меню', callback_data='back_to_start_menu')
    build.adjust(1)
    back_markup = build.as_markup()

    await bot.edit_message_text(text=es_text, chat_id=query.message.chat.id, message_id=query.message.message_id, parse_mode=ParseMode.HTML, reply_markup=back_markup)

