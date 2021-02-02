import asyncio

import aiohttp

from mainapp.add_to_db._base import *
from mainapp.models import atomic, Group, Faculty, Teacher, TeacherNGroup


async def main():
    # серв не дает много подключений за раз. асинк не оч то и нужен...
    session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=2))

    async def _request(offset_=0):
        url = "http://api.rozklad.org.ua/v2/teachers/?filter={'limit':100,'offset':" + str(offset_) + "}"
        async with session.get(url) as resp:
            return await resp.json()

    async def _get_teachers_bunch(offset_):
        return [
            (teacher_['teacher_id'], teacher_)
            for teacher_ in (await _request(offset_))['data']
        ]

    get_group_tasks = [_get_teachers_bunch(offset) for offset in range(0, 5357, 100)]
    teachers_ = {
        int(teacher_id): teacher_
        for teacher_bunch in await asyncio.gather(*get_group_tasks)
        for teacher_id, teacher_ in teacher_bunch
    }

    await session.close()

    with atomic():
        teachers = Teacher.objects.all()
        for t in teachers:
            if t.id > 5332:
                t.name = t.name_position
                t.save()
            else:
                if t.id not in teachers_:
                    continue
                teacher_ = teachers_[t.id]
                t.name = teacher_['teacher_name']
                t.name_position = teacher_['teacher_full_name']
                t.name_position_short = teacher_['teacher_short_name']
                t.save()


asyncio.get_event_loop().run_until_complete(main())