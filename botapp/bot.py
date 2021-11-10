import os
from functools import partial

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage import memory, redis
from aiogram.dispatcher.webhook import DEFAULT_WEB_PATH, get_new_configured_app
from aiogram.utils import executor
from aiohttp import web

from botapp.utils import DeepLinkFilter, opros_state

TOKEN = os.getenv('BOT_TOKEN')

if os.getenv('REDIS_HOST'):
    storage = redis.RedisStorage2(host=os.getenv('REDIS_HOST'))
else:
    storage = memory.MemoryStorage()

bot = Bot(TOKEN, parse_mode='HTML')
dp = Dispatcher(bot, storage=storage)
dp.bind_filter(DeepLinkFilter)

# register handlers
from . import moderate, posting
if opros_state() != '0':
    from . import poll, other_cmds


start_polling = partial(executor.start_polling, dp)


def start_webhook():
    app = get_webapp()
    web.run_app(app, port=os.getenv('bot_port'))


def get_webapp():
    def set_webhook(_):
        return bot.set_webhook(f"https://{os.getenv('BOT_DOMAIN')}{DEFAULT_WEB_PATH}")

    app = get_new_configured_app(dp)
    app.on_startup.append(set_webhook)
    if opros_state() == 'posting':
        app.on_startup.append(lambda _: posting.start_posting())
    # app.on_shutdown.append(on_shutdown)

    return app
