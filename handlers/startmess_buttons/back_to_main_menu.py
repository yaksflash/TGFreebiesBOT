
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

backToMenuRouter = Router()

@backToMenuRouter.callback_query(F.data.startswith('back_to_start_menu'))
async def query_profile_command(query: CallbackQuery):
    hello_text = f'''
❶ Приглашай друзей, пересылай розыгрыши боту и получай звёздочки
❷ Накопи достаточное количество звёздочек и обменяй их на телеграм-подарки!

Дополнительно:
◉ Добавляй папки и участвуй в розыгрышах премиумов и звёзд бесплатно
◉ Участвуй в наших конкурсах на приглашение друзей и добавление розыгрышей
◉ Заходи на наш канал, там часто происходят раздачи

💎 <b>Наш канал:</b> @{CHANNEL_USERNAME}
❤️ <b>Создатель:</b> @{ADMIN_USERNAME}
'''
    
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

    await bot.edit_message_text(text=hello_text, parse_mode=ParseMode.HTML, reply_markup=start_markup, chat_id=query.message.chat.id, message_id=query.message.message_id)
                   