from aiogram.types import Message, CallbackQuery, TelegramObject
from aiogram.enums.chat_member_status import ChatMemberStatus
from aiogram.exceptions import TelegramBadRequest
from aiogram import Bot
from typing import Callable, Awaitable, Dict, Any
from aiogram.enums import ParseMode
from config import CHANNEL_ID, CHANNEL_USERNAME

async def check_subscription(
    handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
    event: TelegramObject,
    data: Dict[str, Any]
) -> Any:
    bot: Bot = data['bot']

    user_id = None
    if isinstance(event, Message):
        user_id = event.from_user.id
        
    elif isinstance(event, CallbackQuery):
        user_id = event.from_user.id
    try:
        if user_id is None:
            return await handler(event, data)
        if user_id != event.chat.id:
            return await handler(event, data)
    except AttributeError:
        return await handler(event, data)
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        if member.status in [ChatMemberStatus.LEFT, ChatMemberStatus.KICKED]:
            raise TelegramBadRequest("User not subscribed")
    except:
        # Если сообщение начинается с /start (в том числе /start=xxx)
        if event.text and event.text.startswith('/start'):
            try:
                _, end = event.text.split(' ')
                text = f'''Привет новичок! 👋
Чтобы пользоваться ботом, подпишись на наш канал:
👉 <a href="https://t.me/{CHANNEL_USERNAME}">Канал</a>
                
А затем снова перейдите по реферальной ссылке, иначе награда не будет начислена:
https://t.me/tg_freebies_bot?start={end}
                '''
            except ValueError:
                text = f'👋 Чтобы пользоваться ботом, подпишись на наш канал и попробуй снова:\n\n👉 <a href="https://t.me/{CHANNEL_USERNAME}">Канал</a>'
            
        else:
            text = f' Чтобы пользоваться ботом, подпишись на наш канал и попробуй снова:\n\n👉 <a href="https://t.me/{CHANNEL_USERNAME}">Канал</a>'
        if isinstance(event, Message):
            await event.answer(text, parse_mode=ParseMode.HTML)
        elif isinstance(event, CallbackQuery):
            await event.message.answer(text, parse_mode=ParseMode.HTML)
        return  # Остановить выполнение хендлера

    return await handler(event, data)