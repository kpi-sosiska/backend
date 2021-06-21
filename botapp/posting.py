import asyncio
from itertools import cycle

from aiogram import types
from aiogram.utils import executor
from aiogram.utils.markdown import hlink

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


async def _send_new_post(faculty, teacher, img_link, comments):
    msg = await _send_post(faculty, teacher, img_link)
    chat_id = await _chat_link_cache(faculty.poll_result_link)

    _comments_queue[(chat_id, msg.text)] = comments


async def _send_post(faculty, teacher, img_link):
    cathedras = ' '.join([
        f"#{cathedra}" for cathedra in
        teacher.cathedras.filter(faculty=faculty).values_list('name')
    ])
    lessons = '\n'.join([
        f"{mark} {lesson};" for lesson, mark
        in zip(teacher.lessons.split('\n'), cycle(('🔹', '🔸')))
    ])
    type_ = "#hui"  # todo

    text = f"{cathedras} {type_} {hlink(teacher.name, 'http://rozklad.kpi.ua/Schedules/ViewSchedule.aspx?v=' + teacher.id)}" \
           f"\n\n{lessons}"
    return await bot.send_photo(faculty.poll_result_link, img_link, caption=text)


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


if __name__ == '__main__':
    import os
    import django

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'garni_studenti.settings')
    django.setup()

    from mainapp.models import Teacher

    teacher = Teacher.objects.all()[0]
    faculty = teacher.groups.all()[0].cathedra.faculty
    faculty.poll_result_link = -1001407513106

    executor.start(dp, send_new_post(faculty, teacher, "https://bbriverboats.com/img/test/3840x2160.png", ["peq1", 'hui2']))
