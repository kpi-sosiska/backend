import logging
import os
from datetime import datetime

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'garni_studenti.settings')
django.setup()

from mainapp.models import Faculty, TeacherFacultyResult
from mainapp.models import Locale as L

import asyncio
from itertools import cycle

from aiogram import types
from aiogram.utils import executor
from aiogram.utils.markdown import hide_link, hlink
from aiogram.utils.exceptions import ChatNotFound, Unauthorized, ChatIdIsEmpty
from pyppeteer import launch

from botapp.bot import dp, bot
from botapp.utils import censure

TEACHER_TYPE = {
    'ENG': '#англ',
    'LECTOR': '#лектор',
    'PRACTIC': '#практик',
    'LECTOR_PRACTIC': '#лектор #практик'
}


async def start_posting():
    print("POSTING ON")
    # todo optimize
    # faculties = Faculty.objects.all().values_list('id')
    faculties = Faculty.objects.filter(name='ФІОТ').values_list('id')

    while True:
        # if not 12 <= datetime.now().hour <= 18:
        #     await asyncio.sleep(60 * 60)  # 1 hour
        #     continue

        tfrs = [TeacherFacultyResult.objects.filter(faculty_id=faculty, message_id__isnull=True).first()
                for faculty in faculties]
        tfrs = filter(None, tfrs)  # remove empty
        if not tfrs:  # no more prepods to post
            return

        for tfr in tfrs:
            logging.info(f"post {tfr.teacher.name} {tfr.faculty.name}")
            try:
                await _post(tfr)
            except:
                logging.exception("posting")
            await asyncio.sleep(5)

        await asyncio.sleep(60 * 60)  # 1 hour


async def _post(tfr):
    cathedras = ' '.join([f"#{cathedra}" for cathedra in tfr.teacher.cathedras.split('\n')])
    lessons = '\n'.join([f"{mark} {lesson};" for lesson, mark
                         in zip(tfr.teacher.lessons.split('\n'), cycle(('🔹', '🔸')))])

    teacher_type = TEACHER_TYPE[tfr.teacher_type]
    teacher_name = tfr.teacher.name
    if tfr.teacher.univer == 1:  # kpi
        teacher_name = hlink(tfr.teacher.name, 'http://rozklad.kpi.ua/Schedules/ViewSchedule.aspx?v=' + tfr.teacher.id)

    text = f"{hide_link(tfr.teacher.id)}" \
           f"{cathedras} {teacher_type} {teacher_name}" \
           f"\n\n{lessons}"

    img = await _get_img(tfr.teacher_id, tfr.faculty_id)
    await bot.send_photo(tfr.faculty.poll_result_link, img, caption=text)


@dp.message_handler(content_types=types.ContentTypes.PHOTO)
async def new_post_handler(message: types.Message):
    if not message.caption_entities or not message.sender_chat:
        return

    teacher_id = message.caption_entities[0].url
    tfr = TeacherFacultyResult.objects.filter(teacher_id=teacher_id,
                                              faculty__poll_result_link=f'@{message.sender_chat.username}').first()
    if not tfr:
        logging.info(f"new_post_handler tfr not found for {teacher_id=} {message.sender_chat.username=}")
        return

    tfr.message_id = message.forward_from_message_id
    tfr.save()

    for comment in tfr.teacher.get_comments(tfr.faculty_id):
        await message.reply(censure(comment))
        await asyncio.sleep(1.5)


async def _get_img(teacher_id, faculty_id):
    browser = await launch({'args': ['--no-sandbox']})
    page = await browser.newPage()
    await page.setViewport(dict(width=1500, height=1500))
    await page.goto(f'https://sova.kpi.in.ua/pic/{teacher_id}/{faculty_id}')
    img = await page.screenshot(type='png')
    await browser.close()
    return img


@dp.message_handler(lambda m: str(m.chat.id) == L['admin_chat_id'], commands=['check'], state='*')
async def check_bot_in_chats(message: types.Message):
    async def check_faculty(channel):
        try:
            member = await bot.get_chat_member(channel, bot.id)
        except ChatNotFound:
            return f'Канала {channel} нету'
        except Unauthorized:
            return f'Бота нету в {channel}'

        if member.status != types.ChatMemberStatus.ADMINISTRATOR:
            return f'Бота нету в {channel}'
        if not member.can_post_messages:
            return f'Бот не имеет права постить в {channel}'

        linked_chat = (await bot.get_chat(channel)).linked_chat_id
        try:
            member = await bot.get_chat_member(linked_chat, bot.id)
        except (ChatNotFound, ChatIdIsEmpty):
            return f'Чата для комментариев у канала {channel} нету'
        except Unauthorized:
            return f'Бота нету в чате для комментариев у канала {channel}'
        if member.can_send_messages is False:
            return f"Бот не имеет права писать в чат для комментариев для {channel}"

        return "OK"

    await message.reply("\n".join([
        f"<b>{faculty.name}</b>: " + await check_faculty(faculty.poll_result_link)
        for faculty in Faculty.objects.all()
    ]))


if __name__ == '__main__':
    async def test():
        tfr = TeacherFacultyResult.objects.filter(faculty__poll_result_link='@svintestchann').first()
        await _post(tfr)

    executor.start_polling(dp, on_startup=[lambda _: test()])
