import asyncio
import re
from typing import Tuple, Optional, Dict, Set
from urllib.parse import quote_plus

import aiohttp

import db
import utils

LESSON_TYPES = {
    'ENG': re.compile(r"інозем|іншомов|ін\. мова", flags=re.IGNORECASE)
}


async def main(force_update=False):
    # серв не дает много подключений за раз. асинк не оч то и нужен...
    session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=2))

    groups_id_to_name = await parse_groups(session)
    if not force_update:
        saved_groups = db.Group.get_groups()
        groups_id_to_name = {k: v for k, v in groups_id_to_name.items() if k not in saved_groups}

    get_teachers_tasks = [parse_teachers(session, group_id) for group_id in groups_id_to_name]
    for task in asyncio.as_completed(get_teachers_tasks):
        group_id, teachers = await task

        if teachers:
            group_name = groups_id_to_name[group_id]
            db.Group.add(group_id, group_name, utils.GroupCode(group_name).faculty)

            for teacher in teachers:
                db.Teacher.add(teacher, group_id)

        print_progress()

    await session.close()


async def parse_groups(session) -> Dict[int, str]:
    async def _request(offset_=0):
        url = "http://api.rozklad.org.ua/v2/groups/?filter={'limit':100,'offset':" + str(offset_) + "}"
        async with session.get(url) as resp:
            return await resp.json()

    async def _get_total_count():
        return int((await _request())['meta']['total_count'])

    async def _get_groups_bunch(offset_):
        return [
            (group_['group_id'], group_['group_full_name'])
            for group_ in (await _request(offset_))['data']
        ]

    get_group_tasks = [_get_groups_bunch(offset) for offset in range(0, await _get_total_count(), 100)]
    return {
        group_id: group_name
        for group_bunch in await asyncio.gather(*get_group_tasks)
        for group_id, group_name in group_bunch
    }


async def parse_teachers(session, group_id) -> Tuple[str, Set[Tuple[Optional[str], str]]]:
    """return (group_name, Set of (teacher_name, teacher_type))"""
    async def _request():
        url = f"http://api.rozklad.org.ua/v2/groups/{quote_plus(str(group_id))}/lessons"
        try:
            async with session.get(url) as resp:
                return await resp.json()
        except (asyncio.exceptions.TimeoutError, aiohttp.ServerDisconnectedError):
            return await _request()

    def _get_teacher(lesson_):
        def _get_type():
            for type__, reg in LESSON_TYPES.items():
                if reg.findall(lesson_['lesson_full_name']):
                    return type__
            return None

        teacher_type = _get_type()
        for teacher in lesson_['teachers']:
            teacher_name = teacher['teacher_full_name'] or teacher['teacher_name']
            yield teacher_name, teacher_type

    res = (await _request())
    if 'data' not in res:
        print(group_id, res)
        return group_id, set()

    teachers = {
        teacher
        for lesson in res['data']
        for teacher in _get_teacher(lesson)
    }
    return group_id, teachers


def print_progress(max_tasks=[0]):  # глобалы - зло
    cur_tasks = len(asyncio.all_tasks())
    max_tasks[0] = max(max_tasks[0], cur_tasks)
    print(f'Осталось обработать: {cur_tasks:> 4}/{max_tasks[0]}')
