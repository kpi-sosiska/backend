from aiogram import types

from botapp.utils import teachers_links, encode_start_group_user, send_other_teachers_in_group, opros_state
from mainapp import models
from mainapp.models import Locale as L
from .bot import dp


@dp.message_handler(commands=['start'], state='*', deep_link='g')
async def start_group(message: types.Message, payload: str):
    try:
        group = models.Group.objects.get(id=payload)
    except models.Group.DoesNotExist:
        return await message.answer(L['wrong_link'])

    teachers = group.teacher_need_votes()
    text = L['group_teachers_text' + opros_state()].format(
        group_name=group.name.upper(),
        results_link=group.faculty.poll_result_link,
        teachers=teachers_links(teachers),
        start_group_link=encode_start_group_user(group.id))
    await message.reply(text)


@dp.message_handler(commands=['start'], state='*', deep_link='gu')
async def start_group_user(message: types.Message, payload: str):
    try:
        group = models.Group.objects.get(id=payload)
    except models.Group.DoesNotExist:
        return await message.answer(L['wrong_link'])

    await send_other_teachers_in_group(message, group)


@dp.message_handler(commands=['start'], state='*')
async def start_fallback(message: types.Message):
    await message.answer(L['wrong_link'] if message.get_args() else L['unknown_cmd'])


@dp.message_handler(commands=['help'], state='*')
async def help_cmd(message: types.Message):
    await message.answer(L['help_text'])


@dp.message_handler(state='*', chat_type=types.ChatType.PRIVATE)
async def text_fallback(message: types.Message):
    await message.answer(L['unknown_cmd'])


@dp.callback_query_handler(state='*')
async def query_fallback(query: types.CallbackQuery):
    await query.answer(L['callback_no_state'], show_alert=True)
