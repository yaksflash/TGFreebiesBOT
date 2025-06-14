
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

from config import CHANNEL_CHAT_USERNAME, ADMIN_USERNAME
from config import ADMIN_STARS_GROUP
smInformationRouter = Router()

@smInformationRouter.callback_query(F.data.startswith('startmess-info'))
async def information_button(query: CallbackQuery):
    info_text = f'''
Основная информация о нашем проекте:
https://telegra.ph/TG-Freebies--Kratkij-FAQ-05-13

Если у вас есть какой-либо вопрос, то вы можете просто его написать и отправить боту: ИИ-ассистент вам подскажет. Также можете задать свой вопрос в нашем чате или лично администратору проекта.

Чат: @{CHANNEL_CHAT_USERNAME}
Админ: @{ADMIN_USERNAME}
'''
    
    build = InlineKeyboardBuilder()
    build.button(text='назад в меню', callback_data='back_to_start_menu')
    build.adjust(1)
    back_markup = build.as_markup()

    await bot.edit_message_text(text=info_text, chat_id=query.message.chat.id, message_id=query.message.message_id, parse_mode=ParseMode.HTML, reply_markup=back_markup, disable_web_page_preview=True)

