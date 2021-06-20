import urllib.request
from functools import partial
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.webhook import DEFAULT_WEB_PATH, get_new_configured_app
from aiogram.utils import executor
from aiohttp import web

from botapp.utils import DeepLinkFilter

TOKEN = getenv('bot_token')
storage = MemoryStorage()

bot = Bot(TOKEN, parse_mode='HTML')
dp = Dispatcher(bot, storage=storage)
dp.bind_filter(DeepLinkFilter)

# register handlers
from . import poll, other_cmds


start_polling = partial(executor.start_polling, dp)


def start_webhook():
    def get_ip():
        with urllib.request.urlopen("http://api.ipify.org/") as response:
            return response.read().decode('ascii')

    def set_webhook(_):
        return bot.set_webhook(f"https://{get_ip()}{DEFAULT_WEB_PATH}")

    app = get_new_configured_app(dp)
    # app.add_routes([web.get('/url', handler)])  # todo maybe posting signal here

    app.on_startup.append(set_webhook)
    # app.on_shutdown.append(on_shutdown)
    web.run_app(app, port=getenv('bot_port'))
