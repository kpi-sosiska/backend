import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'garni_studenti.settings')
django.setup()

from mainapp.models import Faculty, Teacher, TeacherFacultyResult

import asyncio
from itertools import cycle

from aiogram import types
from aiogram.utils import executor
from aiogram.utils.markdown import hide_link, hlink
from pyppeteer import launch

from botapp.bot import dp, bot

TEACHER_TYPE = {
    'ENG': '#англ',
    'LECTOR': '#лектор',
    'PRACTIC': '#практик',
    'LECTOR_PRACTIC': '#лектор #практик'
}


async def make_new_post():
    teacher = Teacher.objects.filter(teacherfacultyresult=None).first()  # todo
    teacher.type = teacher.get_results()['teacher_type']
    img = _get_img(teacher.slug)

    for faculty in teacher.get_faculties():
        await _send_post(faculty, teacher, img)


async def _send_post(faculty, teacher, img):
    cathedras = ' '.join([f"#{cathedra}" for cathedra in teacher.cathedras.split('\n')])
    lessons = '\n'.join([f"{mark} {lesson};" for lesson, mark
                         in zip(teacher.lessons.split('\n'), cycle(('🔹', '🔸')))])

    teacher_type = TEACHER_TYPE[teacher.type]
    teacher_name = teacher.name
    if teacher.univer == 1:  # kpi
        teacher_name = hlink(teacher.name, 'http://rozklad.kpi.ua/Schedules/ViewSchedule.aspx?v=' + teacher.id)

    text = f"{hide_link(teacher.id)}" \
           f"{cathedras} {teacher_type} {teacher_name}" \
           f"\n\n{lessons}"
    return await bot.send_photo(faculty.poll_result_link, img, caption=text)


@dp.channel_post_handler()
async def new_post_handler(message: types.Message):
    if not message.caption_entities or not message.sender_chat:
        return

    teacher_id = message.caption_entities[0].url
    faculty_chat = '@' + message.sender_chat.username

    try:
        faculty = Faculty.objects.get(poll_result_link=faculty_chat)
    except Faculty.DoesNotExist:
        return

    tfr = TeacherFacultyResult(teacher_id=teacher_id, faculty=faculty,
                               message_id=message.message_id)
    tfr.save()

    for comment in tfr.teacher.get_comments():
        await message.reply(comment)
        await asyncio.sleep(1.5)


async def _get_img(teacher_id):
    browser = await launch()
    page = await browser.newPage()
    await page.setViewport(dict(width=1500, height=1500))
    await page.goto('https://sova.kpi.in.ua/pic/' + teacher_id)
    img = await page.screenshot(type='png')
    await browser.close()
    return img


if __name__ == '__main__':
    teacher = Teacher.objects.get(id='d1bfd5d9-efde-40af-992e-7f8e798a5f69')
    faculty = teacher.get_faculties()[0]

    async def test():
        img = await _get_img(teacher.id)
        await _send_post(faculty, teacher, img)


    executor.start(dp, test())
