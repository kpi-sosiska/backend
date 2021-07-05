import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'garni_studenti.settings')
django.setup()

from mainapp.models import Faculty, Teacher


import asyncio
from itertools import cycle

from aiogram import types
from aiogram.utils import executor
from aiogram.utils.markdown import hlink
from pyppeteer import launch

from botapp.bot import dp, bot

TEACHER_TYPE = {
    'LECTOR': '#лектор',
    'PRACTIC': '#практик',
    'LECTOR_PRACTIC': '#лектор #практик'
}
_comments_queue = {}


async def make_new_post():
    pass
    # todo


async def _send_new_post(faculty, teacher, img, comments):
    msg = await _send_post(faculty, teacher, img)
    chat_id = await _chat_link_cache(faculty.poll_result_link)

    _comments_queue[(chat_id, msg.text)] = comments


async def _send_post(faculty, teacher, img):
    cathedras = ' '.join([
        f"#{cathedra}" for cathedra in
        teacher.cathedras.filter(faculty=faculty).values_list('name', flat=True)
    ])
    lessons = '\n'.join([
        f"{mark} {lesson};" for lesson, mark
        in zip(teacher.lessons.split('\n'), cycle(('🔹', '🔸')))
    ])
    type_ = "#hui"  # todo

    text = f"{cathedras} {type_} {hlink(teacher.name, 'http://rozklad.kpi.ua/Schedules/ViewSchedule.aspx?v=' + teacher.id)}" \
           f"\n\n{lessons}"
    return await bot.send_photo(faculty.poll_result_link, img, caption=text)


@dp.channel_post_handler()
async def new_post_handler(message: types.Message):
    comments = _comments_queue.get((message.chat.id, message.text), None)
    if comments is None:
        return

    for comment in comments:
        await message.reply(comment)
        await asyncio.sleep(1.5)


async def _chat_link_cache(channel, cache={}):
    if channel not in cache:
        chat_id = (await bot.get_chat(channel)).linked_chat_id
        cache[channel] = chat_id
    return cache[channel]


async def _get_img():
    browser = await launch()
    page = await browser.newPage()
    await page.setViewport(dict(width=1500, height=1500))
    await page.goto('https://sova.kpi.in.ua/pic/')
    img = await page.screenshot(type='png')
    await browser.close()
    return img

if __name__ == '__main__':
    faculty = Faculty.objects.get(id=10106)
    faculty.poll_result_link = -1001407513106

    teacher = Teacher.objects.get(id='d1bfd5d9-efde-40af-992e-7f8e798a5f69')

    async def test():
        img = await _get_img()
        await _send_new_post(faculty, teacher, img, ["peq1", 'hui2'])

    executor.start(dp, test())
