from aiogram import types

from mainapp import models
from .bot import dp
from botapp.utils import make_group_teachers_text


@dp.message_handler(commands=['group'])
async def make_group_teachers_text_handler(message: types.Message):
    group_name = message.get_args()
    try:
        text = make_group_teachers_text(group_name)
    except models.Group.DoesNotExist:
        await message.answer('Нет такой группы')
    except models.Group.MultipleObjectsReturned:
        await message.answer('Под этот запрос подходит несколько групп')
    else:
        await message.reply(text)
