import asyncio
import json
from contextlib import suppress
from typing import Tuple

from aiogram import types, exceptions
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.markdown import hbold, hitalic, hide_link

from botapp.utils import hash_, question_keyboard, teachers_links
from mainapp import models
from mainapp.models import Locale as L
from .bot import dp


class PollStates(StatesGroup):
    teacher_type = State()
    questions = State()
    open_question = State()

    two_group_one_user = State()


"""
data:
    teacher_n_group = teacher
    teacher_type = ...
    q2a = dict(
        question_id: None
        question_id: user answer
    )
    open_q = user answ
"""


@dp.message_handler(commands=['start'], state='*', deep_link='t')
async def start_poll(message: types.Message, state: FSMContext, payload: Tuple[str, str]):
    teacher_id, group_id = payload
    try:
        teacher_n_group = models.TeacherNGroup.objects.get(teacher_id=teacher_id, group_id=group_id)
    except (ValueError, models.TeacherNGroup.DoesNotExist):
        return await message.answer(L['wrong_link'])

    await state.set_data(dict(teacher_n_group=teacher_n_group))

    # если у челика есть прохождения опроса с других групп то предупреждаем
    if await two_group_one_user(message, state):
        return

    if models.Result.filter_finished().filter(user_id=hash_(message.from_user.id),
                                              teacher_n_group=teacher_n_group).count():
        await message.answer(L['same_teacher_again'])

    await start_teacher(message, state)


async def start_teacher(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        teacher = data['teacher_n_group'].teacher

    # save poll started
    models.Result(user_id=hash_(message.from_user.id), teacher_n_group=data['teacher_n_group']).save()

    await message.answer(hide_link(teacher.photo) + L['teacher_text'].format(teacher=teacher))
    if teacher.is_eng:
        await state.update_data(teacher_type='ENG')
        await questions_start(message, state)
    else:
        await teacher_type_start(message)


async def teacher_type_start(message: types.Message):
    keyboard = types.InlineKeyboardMarkup(row_width=2).add(*[
        types.InlineKeyboardButton(L[f'teacher_type_{type_}'], callback_data=type_)
        for type_ in list(models.TEACHER_TYPE.keys())[:-1]  # типы кроме англ
    ])
    await message.answer(L['choose_teacher_type'], reply_markup=keyboard)
    await PollStates.teacher_type.set()


@dp.callback_query_handler(state=PollStates.teacher_type)
async def teacher_type_query_handler(query: types.CallbackQuery, state: FSMContext):
    type_ = query.data
    if type_ not in list(models.TEACHER_TYPE.keys())[:-1]:
        return await query.answer("?")

    await query.answer()
    await state.update_data(teacher_type=type_)
    await query.message.edit_text(L['teacher_type_chosen'].format(type=L[f'teacher_type_{type_}']))
    await questions_start(query.message, state)


async def questions_start(message: types.Message, state: FSMContext):
    async def _send_msg(question_):
        for _ in range(5):
            try:
                text = hbold(question_.question_text) + \
                       ('\n\n' + hitalic(question_.answer_tip) if question.answer_tip else '')
                await message.answer(text, reply_markup=question_keyboard(question_, teacher_type))
                await asyncio.sleep(0.1)
                return
            except exceptions.RetryAfter as ex:
                await asyncio.sleep(ex.timeout + 1)

    async with state.proxy() as data:
        teacher_type = data['teacher_type']
        data['q2a'] = {}

        questions = models.Question.get_by_type(teacher_type)
        for question in questions:
            await _send_msg(question)
            data['q2a'][question.id] = [None] * (2 if question.need_two_answers(teacher_type) else 1)

    await PollStates.questions.set()


@dp.callback_query_handler(state=PollStates.questions)
async def questions_handler(query: types.CallbackQuery, state: FSMContext):
    question_id, row_n, answer = json.loads(query.data)
    await query.answer()

    async with state.proxy() as data:
        data['q2a'][question_id][row_n] = answer

    keyboard = question_keyboard(models.Question.objects.get(id=question_id),
                                 teacher_type=data['teacher_type'], answers=data['q2a'][question_id])
    with suppress(exceptions.MessageNotModified):
        await query.message.edit_reply_markup(keyboard)

    if all(answer is not None for answers in data['q2a'].values() for answer in answers):
        await open_question_start(query.message)


async def open_question_start(message: types.Message):
    await message.answer(L['open_question_text'], reply_markup=types.ForceReply())
    await PollStates.open_question.set()


@dp.message_handler(state=PollStates.open_question)
async def open_question_query_handler(message: types.Message, state: FSMContext):
    if message.text in ('/skip', '/confirm'):
        if message.text == '/skip':
            await state.update_data(open_q=None)
        await save_to_db(message, state)
        await other_teachers_in_group(message, state)
        await state.finish()
    else:
        await state.update_data(open_q=message.text)
        await message.answer(L['confirm_open_question_text'])


async def save_to_db(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        try:
            models.Result.add(hash_(message.from_user.id), data['teacher_n_group'],
                              data['teacher_type'], data['open_q'], data['q2a'])
        except Exception:
            await message.answer(L['result_save_error'], reply_markup=types.ReplyKeyboardRemove())
            raise
        else:
            await message.answer(L['result_save_success'], reply_markup=types.ReplyKeyboardRemove())


#


async def other_teachers_in_group(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        group = data['teacher_n_group'].group

    # преподы которых еще нужно пройти отсортированные по кол-ву прохождений
    teachers = group.teacher_need_votes(). \
        exclude(teacherngroup__result__user_id=hash_(message.from_user.id),
                teacherngroup__result__time_finish__isnull=False)

    if teachers:
        teachers = teachers_links(teachers, group.id)
        text = L['other_teachers_in_group_text'].format(group_name=group.name.upper(), teachers=teachers)
        await message.answer(text)


#


KEYBOARD_2G1U = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(L['btn_reset_2g1u'], callback_data='reset'))


async def two_group_one_user(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        teacher_n_group = data['teacher_n_group']

    results_from_other_group = models.Result.filter_finished().filter(user_id=hash_(message.from_user.id)) \
        .exclude(teacher_n_group__group=teacher_n_group.group)

    if not results_from_other_group:
        return False

    cur_group = teacher_n_group.group.name.upper()
    other_group = results_from_other_group[0].teacher_n_group.group.name.upper()

    await message.answer(
        L['two_group_one_user'].format(other_group=other_group, cur_group=cur_group),
        reply_markup=KEYBOARD_2G1U
    )
    await PollStates.two_group_one_user.set()
    return True


@dp.callback_query_handler(state=PollStates.two_group_one_user)
async def two_group_one_user_handler(query: types.CallbackQuery, state: FSMContext):
    await query.answer()
    if query.data != 'reset':
        return

    async with state.proxy() as data:
        teacher_n_group = data['teacher_n_group']
    models.Result.objects.filter(user_id=hash_(query.from_user.id)) \
        .exclude(teacher_n_group__group=teacher_n_group.group).delete()
    await query.message.edit_reply_markup()
    await start_teacher(query.message, state)
