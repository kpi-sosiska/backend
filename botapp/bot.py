from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

TOKEN = "504692764:AAHz6mfa7pXfArb9fcY_dxn4C2yA2vYYIJA"

storage = MemoryStorage()
bot = Bot(TOKEN, parse_mode='HTML')
dp = Dispatcher(bot, storage=storage)

