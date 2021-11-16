import io
import logging
import os
from contextlib import suppress
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
    faculties = Faculty.objects.all().values_list('id')
    # faculties = Faculty.objects.filter(name='ФІОТ').values_list('id')
    while True:
        if not 11 <= datetime.now().hour <= 19:
            print('skip posting')
            await asyncio.sleep(30 * 60)  # 30 min
            continue

        tfrs = [TeacherFacultyResult.objects.filter(faculty_id=faculty, message_id__isnull=True).first()
                for faculty in faculties]
        print(tfrs)
        tfrs = filter(None, tfrs)  # remove empty
        if not tfrs:  # no more prepods to post
            return

        for tfr in tfrs:
            print(f"post {tfr.teacher.name} {tfr.faculty.name}")
            try:
                await _post(tfr)
            except:
                logging.exception("posting")
            await asyncio.sleep(5)

        await asyncio.sleep(30 * 60)  # 30 min


async def _get_photo_and_text(tfr):
    if not tfr.teacher.cathedras:
        tfr.teacher.cathedras = ''
    if not tfr.teacher.lessons or not tfr.teacher.lessons.strip():
        tfr.teacher.lessons = ''

    cathedras = ' '.join([f"#{cathedra}" for cathedra in tfr.teacher.cathedras.split('\n') if cathedra])
    lessons = '\n'.join([f"{mark} {lesson}" for lesson, mark
                         in zip(tfr.teacher.lessons.split('\n'), cycle(('🔹', '🔸'))) if lesson])

    teacher_type = TEACHER_TYPE[tfr.teacher_type]
    teacher_name = tfr.teacher.name
    if tfr.teacher.univer == 1:  # kpi
        teacher_name = hlink(tfr.teacher.name, 'http://rozklad.kpi.ua/Schedules/ViewSchedule.aspx?v=' + tfr.teacher.id)

    text = f"{hide_link('http://teacher.com/' + tfr.teacher.id)}" \
           f"{cathedras} {teacher_type} {teacher_name}" \
           f"\n\n{lessons}"
    img = await _get_img(tfr.teacher_id, tfr.faculty_id)
    return img, text


async def _post(tfr):
    img, text = await _get_photo_and_text(tfr)
    message = await bot.send_photo(tfr.faculty.poll_result_link, img, caption=text, disable_notification=True)
    tfr.message_id = message.message_id
    tfr.save()


@dp.message_handler(commands=['post_comments'])
async def post_comments_handler(message: types.Message):
    tfr = await _get_tfr(message)
    if not tfr:
        return

    with suppress(Exception):
        await message.delete()

    comments = tfr.teacher.get_comments(tfr.faculty_id)
    if not comments:
        return await message.reply("Комментов нема")
    for comment in comments:
        await message.reply_to_message.reply(censure(comment[0]))
        await asyncio.sleep(1.5)


@dp.message_handler(commands=['update_photo'])
async def update_photo_handler(message: types.Message):
    tfr = await _get_tfr(message)
    if not tfr:
        return

    with suppress(Exception):
        await message.delete()

    img, text = await _get_photo_and_text(tfr)
    await bot.edit_message_media(types.InputMediaPhoto(io.BytesIO(img), caption=text, parse_mode='HTML'),
                                 tfr.faculty.poll_result_link, tfr.message_id)


async def _get_tfr(message: types.Message):
    channel_post = message.reply_to_message
    if not channel_post:
        return

    if not (await channel_post.forward_from_chat.get_member(message.from_user.id)).is_chat_admin():
        return

    return TeacherFacultyResult.objects.filter(faculty__poll_result_link=f'@{channel_post.forward_from_chat.username}',
                                               message_id=channel_post.forward_from_message_id).first()


@dp.message_handler(lambda m: m.forward_from_message_id, content_types=types.ContentTypes.PHOTO)
async def new_post_handler(message: types.Message):
    tfr = TeacherFacultyResult.objects.filter(faculty__poll_result_link=f'@{message.sender_chat.username}',
                                              message_id=message.forward_from_message_id).first()
    if not tfr:
        print(f"new_post_handler tfr not found for {message.forward_from_message_id=} {message.sender_chat.username=}")
        return
    print(f"prepod {message.forward_from_message_id=} {message.sender_chat.username=} posted")

    for comment in tfr.teacher.get_comments(tfr.faculty_id):
        await message.reply(censure(comment[0]))
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
        asyncio.ensure_future(start_posting())


    executor.start_polling(dp, on_startup=[lambda _: test()])
