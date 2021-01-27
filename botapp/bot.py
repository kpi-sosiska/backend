import asyncio
import json
import sys
import traceback
from os import getenv

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from django.http import HttpResponse

from botapp.utils import DeepLinkFilter

TOKEN = getenv('bot_token')

storage = MemoryStorage()
bot = Bot(TOKEN, parse_mode='HTML')
dp = Dispatcher(bot, storage=storage)

dp.bind_filter(DeepLinkFilter)


# register handlers
from . import poll, other_cmds


def set_webhook(url):
    asyncio.run(bot.set_webhook(url))


async def webhook_update(request):
    update_data = json.loads(request.body)
    try:
        Bot.set_current(bot)
        Dispatcher.set_current(dp)
        update_data = types.Update(**update_data)
        await dp.process_updates([update_data])
    except Exception:
        traceback.print_exception(*sys.exc_info())

    return HttpResponse('ok')
