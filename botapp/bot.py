from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from botapp.utils import DeepLinkFilter

TOKEN = getenv('bot_token')

storage = MemoryStorage()
bot = Bot(TOKEN, parse_mode='HTML')
dp = Dispatcher(bot, storage=storage)

dp.bind_filter(DeepLinkFilter)
