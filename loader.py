from config import TOKEN

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

bot = Bot(token="7937832762:AAERMuGKuYkx2H2-9O3GaoRYn5cY-jQpjMI")
dp = Dispatcher(storage=MemoryStorage())
