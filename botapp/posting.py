import logging
import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'garni_studenti.settings')
django.setup()

from mainapp.models import Faculty, TeacherFacultyResult

import asyncio
from itertools import cycle

from aiogram import types
from aiogram.utils import executor
from aiogram.utils.markdown import hide_link, hlink
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
    while True:
        # todo optimize
        faculties = Faculty.objects.all().values_list('id')
        tfrs = [TeacherFacultyResult.objects.filter(faculty_id=faculty, message_id__isnull=True).first()
                for faculty in faculties]
        tfrs = filter(None, tfrs)  # remove empty
        if not tfrs:  # no more prepods to post
            return

        for tfr in tfrs:
            logging.info(f"post {tfr.teacher.name} {tfr.faculty.name}")
            await _post(tfr)
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

    for comment in tfr.teacher.get_comments():
        await message.reply(censure(comment))
        await asyncio.sleep(1.5)


async def _get_img(teacher_id, faculty_id):
    browser = await launch()
    page = await browser.newPage()
    await page.setViewport(dict(width=1500, height=1500))
    await page.goto(f'https://sova.kpi.in.ua/pic/{teacher_id}/{faculty_id}')
    img = await page.screenshot(type='png')
    await browser.close()
    return img


if __name__ == '__main__':
    async def test():
        tfr = TeacherFacultyResult.objects.filter(faculty__poll_result_link='@svintestchann').first()
        await _post(tfr)

    executor.start_polling(dp, on_startup=[lambda _: test()])
