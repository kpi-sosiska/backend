from typing import Tuple

from aiogram import types

from botapp.utils import teachers_links
from mainapp import models
from mainapp.models import Locale as L
from .bot import dp


@dp.message_handler(commands=['start'], state='*', deep_link='g')
async def start_group(message: types.Message, payload: Tuple[str]):
    group_id = payload[0]
    try:
        group = models.Group.objects.get(id=group_id)
    except models.Group.DoesNotExist:
        return await message.answer(L['wrong_link'])

    teachers = group.teacher_need_votes()
    teachers = teachers_links(teachers, group.id)
    text = L['group_teachers_text'].format(group_name=group.name.upper(),
                                           results_link=group.faculty.poll_result_link, teachers=teachers)
    await message.reply(text)


@dp.message_handler(commands=['start'], state='*')
async def start_fallback(message: types.Message):
    await message.answer(L['wrong_link'] if message.get_args() else L['unknown_cmd'])


@dp.message_handler(commands=['help'], state='*')
async def help_cmd(message: types.Message):
    await message.answer(L['help_text'])


@dp.message_handler(state='*')
async def text_fallback(message: types.Message):
    await message.answer(L['unknown_cmd'])


@dp.callback_query_handler(state='*')
async def query_fallback(query: types.CallbackQuery):
    await query.answer(L['callback_no_state'], show_alert=True)
