from typing import Tuple

from aiogram import types
from aiogram.utils.markdown import hlink

from botapp.utils import encode_start_teacher
from mainapp import models
from mainapp.models import Locale as L
from .bot import dp


@dp.message_handler(commands=['start'], state='*', deep_link='g')
async def start_group(message: types.Message, payload: Tuple[str]):
    group_id = int(payload[0])
    try:
        group = models.Group.objects.get(id=group_id)
    except models.Group.DoesNotExist:
        return await message.answer('Нет такой группы')

    teachers = [
        '• ' + hlink(t.name, encode_start_teacher(t.id, group.id))
        for t in group.teachers.all()
    ]
    text = L['group_teachers_text'].format(
        group_name=group.name.upper(), results_link=group.faculty.poll_result_link, teachers='\n'.join(teachers)
    )
    await message.reply(text)


@dp.message_handler(commands=['start'], state='*')
async def start_fallback(message: types.Message):
    await message.answer(L['no_start_cmd'])
