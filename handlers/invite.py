
from aiogram import Router, F, types
from aiogram.types import Message
from aiogram.filters import Command

from datetime import datetime, timedelta
import sqlite3
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

import pytz

from aiogram.types import FSInputFile


inviteRouter = Router()


@inviteRouter.message(Command('invite'))
async def invite_command(message: Message):
    user_link = f'https://t.me/tg_freebies_bot?start=ref_{message.from_user.id}'
    invite_text = f'''
 <b>👥 Реферальная система 👥</b>
Чтобы пригласить друга, воспользуйтесь своей персональной ссылкой:
 <code>{user_link}</code>

<i>Нажмите на неё, чтобы скопировать или воспользуйтесь кнопкой "отправить ссылку"</i>

'''
    builder = InlineKeyboardBuilder()

    builder.button(text='🌐 Отправить ссылку', url=f'https://t.me/share/url?url=%D0%9F%D1%80%D0%B8%D0%B2%D0%B5%D1%82!%20%F0%9F%91%8B%20%D0%A5%D0%BE%D1%87%D0%B5%D1%88%D1%8C%20%D0%BF%D0%BE%D0%BB%D1%83%D1%87%D0%B8%D1%82%D1%8C%20%D1%82%D0%B5%D0%BB%D0%B5%D0%B3%D1%80%D0%B0%D0%BC%20%D0%BF%D1%80%D0%B5%D0%BC%D0%B8%D1%83%D0%BC%20%D0%B8%D0%BB%D0%B8%20%D0%B7%D0%B2%D1%91%D0%B7%D0%B4%D1%8B?%20%D0%9F%D0%B5%D1%80%D0%B5%D1%85%D0%BE%D0%B4%D0%B8%20%D0%B2%20%D1%8D%D1%82%D0%BE%D0%B3%D0%BE%20%D0%B1%D0%BE%D1%82%D0%B0:\n{user_link}')

    ref_markup = builder.as_markup(resize_keyboard=True)

    photo = FSInputFile(path="images/referal_banner.jpg")
    await message.answer(text=invite_text, parse_mode=ParseMode.HTML, reply_markup=ref_markup)
