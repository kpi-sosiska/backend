import asyncio
import logging
from contextlib import suppress

from aiogram import types, exceptions
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.markdown import hbold, hitalic, hide_link

from botapp.utils import hash_, question_keyboard, cb_answer, cb_help, try_send, \
    send_other_teachers_in_group
from mainapp import models
from mainapp.models import Locale as L
from .bot import dp


class PollStates(StatesGroup):
    teacher_type = State()
    questions = State()
    open_question = State()

    two_group_one_user = State()
    same_teacher_again = State()


"""
data:
    teacher_n_group: int = teacher_n_group.id
    result: int = models.Result object
    
    teacher_type: str = one of models.TEACHER_TYPE
    open_question: str = open question user answer 
    
    q2a = dict(                # question_id: List[Optional[int]]
        question_1: [4, 5]     # 2 questions, 2 answers
        question_4: [1, None]  # 2 questions, 1 answers
        question_3: [None]     # 1 questions, 0 answers
    )
"""


@dp.message_handler(commands=['start'], state='*', deep_link='t')
async def start_poll(message: types.Message, state: FSMContext, payload: str):
    try:
        teacher_n_group = models.TeacherNGroup.objects.get(id=payload)
    except (ValueError, models.TeacherNGroup.DoesNotExist):
        return await message.answer(L['wrong_link'])

    async with state.proxy() as data:
        data['teacher_n_group'] = payload
        result = models.Result(user_id=hash_(message.from_user.id), teacher_n_group=teacher_n_group)
        result.save()  # save result now to have time_start and id
        data['result'] = result.id

    # если у челика есть прохождения опроса с других групп то предупреждаем
    if await two_group_one_user(message, state):
        return

    # если челик перепроходит препода
    if await same_teacher_again(message, state):
        return

    await start_teacher(message, state)


async def start_teacher(message: types.Message, state: FSMContext):
    tng = models.TeacherNGroup.objects.get(id=(await state.get_data())['teacher_n_group'])

    await message.answer(hide_link(tng.teacher.photo) + L['teacher_text'].format(teacher=tng.teacher))

    if tng.teacher.is_eng:
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

    await state.update_data(teacher_type=type_)

    await query.answer()
    await query.message.edit_text(L['teacher_type_chosen'].format(type=L[f'teacher_type_{type_}']))
    await questions_start(query.message, state)


async def questions_start(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        teacher_type = data['teacher_type']
        data['q2a'] = {}

        questions = models.Question.get_by_type(teacher_type)
        for question in questions:
            if not await try_send(message.answer, hbold(question.question_text),
                                  reply_markup=question_keyboard(question, teacher_type)):
                return await message.answer(L['result_save_error'])  # if can't send message in 5 attempts
            await asyncio.sleep(0.1)

            data['q2a'][question.name] = [None] * (2 if question.need_two_answers(teacher_type) else 1)

    await PollStates.questions.set()


@dp.callback_query_handler(cb_answer.filter(), state=[PollStates.questions, PollStates.open_question])
async def questions_handler(query: types.CallbackQuery, state: FSMContext, callback_data: dict):
    question, row_n, answer = callback_data['question'], int(callback_data['row']), int(callback_data['answer'])
    async with state.proxy() as data:
        data['q2a'][question][row_n] = answer

    keyboard = question_keyboard(models.Question.objects.get(name=question), teacher_type=data['teacher_type'],
                                 answers=data['q2a'][question],
                                 hide_help=query.message.reply_markup.inline_keyboard[-1][-1].text != "❓")
    with suppress(exceptions.MessageNotModified):
        await query.message.edit_reply_markup(keyboard)

    answers_left = sum(1 for answers in data['q2a'].values() for answer in answers if answer is None)
    if answers_left == 0 and await state.get_state() != PollStates.open_question.state:
        await query.answer()
        return await open_question_start(query.message)
    if answers_left <= 3:
        await query.answer(L['answers_left'].format(answers_left))
    await query.answer()


@dp.callback_query_handler(cb_help.filter(question='2answ'), state='*')
async def questions_handler(query: types.CallbackQuery):
    await query.answer(L['2answ_help'])


@dp.callback_query_handler(cb_help.filter(), state=[PollStates.questions, PollStates.open_question])
async def questions_handler(query: types.CallbackQuery, state: FSMContext, callback_data: dict):
    q = models.Question.objects.get(name=callback_data['question'])
    data = await state.get_data()
    text = hbold(q.question_text) + ('\n\n' + hitalic(q.answer_tip) if q.answer_tip else '')
    keyboard = question_keyboard(q, teacher_type=data['teacher_type'], answers=data['q2a'][q.name], hide_help=True)
    await query.message.edit_text(text, reply_markup=keyboard)


async def open_question_start(message: types.Message):
    await message.answer(L['open_question_text'], reply_markup=types.ForceReply())
    await PollStates.open_question.set()


@dp.message_handler(state=PollStates.open_question)
async def open_question_query_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text not in ('/skip', '/confirm'):
            data['open_question'] = message.text
            return await message.answer(L['confirm_open_question_text'])

        if message.text == '/skip':
            data['open_question'] = None

    await save_to_db(message, data)
    await send_other_teachers_in_group(
        message, models.TeacherNGroup.objects.get(id=data['teacher_n_group']).group)
    await state.finish()


async def save_to_db(message: types.Message, data: dict):
    try:
        models.Result.objects.get(id=data['result']).finish(
            teacher_type=data['teacher_type'],
            open_question_answer=data['open_question'],
            other_answers=data['q2a'])
    except Exception:
        await message.answer(L['result_save_error'], reply_markup=types.ReplyKeyboardRemove())
        logging.exception("Failed to save")
    else:
        await message.answer(L['result_save_success'], reply_markup=types.ReplyKeyboardRemove())


#

KEYBOARD_STA = types.InlineKeyboardMarkup().add(
    types.InlineKeyboardButton(L['btn_sta_reset'], callback_data='sta_reset'),
    types.InlineKeyboardButton(L['btn_sta_copy'], callback_data='sta_copy')
)


async def same_teacher_again(message: types.Message, state: FSMContext):
    if models.Result.objects.filter(is_active=True, user_id=hash_(message.from_user.id),
                                    teacher_n_group_id=(await state.get_data())['teacher_n_group']).exists():
        await message.answer(L['same_teacher_again'], reply_markup=KEYBOARD_STA)
        await PollStates.same_teacher_again.set()
        return True
    return False


@dp.callback_query_handler(lambda q: q.data.startswith('sta'), state=PollStates.same_teacher_again)
async def same_teacher_again_handler(query: types.CallbackQuery, state: FSMContext):
    await query.answer()
    await query.message.edit_reply_markup()

    if query.data == 'sta_reset':
        return await start_teacher(query.message, state)

    async with state.proxy() as data:
        result = models.Result.objects.filter(is_active=True, user_id=hash_(query.from_user.id),
                                              teacher_n_group_id=data['teacher_n_group']).first()
        data['teacher_type'] = result.teacher_type
        data['q2a'] = {}

        # copy from questions_start
        for a in result.answers.all():
            answers = [a.answer_1, a.answer_2]
            if not await try_send(query.message.answer, hbold(a.question.question_text),
                                  reply_markup=question_keyboard(a.question, result.teacher_type, answers)):
                return await query.message.answer(L['result_save_error'])  # if can't send message in 5 attempts
            await asyncio.sleep(0.1)
            data['q2a'][a.question.name] = [i for i in answers if i is not None]

        if result.open_question_answer:
            await query.message.answer(L['open_question_text_old'])
            await query.message.answer(result.open_question_answer)

    await open_question_start(query.message)


#

KEYBOARD_2G1U = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(L['btn_reset_2g1u'], callback_data='reset'))


async def two_group_one_user(message: types.Message, state: FSMContext):
    tng = models.TeacherNGroup.objects.get(id=(await state.get_data())['teacher_n_group'])
    results_from_other_group = _2g1u_results(message.from_user.id, tng)
    if not results_from_other_group:
        return False

    cur_group = tng.group.name.upper()
    other_group = results_from_other_group[0].teacher_n_group.group.name.upper()
    await message.answer(L['two_group_one_user'].format(other_group=other_group, cur_group=cur_group),
                         reply_markup=KEYBOARD_2G1U)

    await PollStates.two_group_one_user.set()
    return True


@dp.callback_query_handler(state=PollStates.two_group_one_user)
async def two_group_one_user_handler(query: types.CallbackQuery, state: FSMContext):
    await query.answer()
    if query.data != 'reset':
        return

    tng = models.TeacherNGroup.objects.get(id=(await state.get_data())['teacher_n_group'])
    _2g1u_results(query.from_user.id, tng).update(is_active=False)

    await query.message.edit_reply_markup()
    await start_teacher(query.message, state)


def _2g1u_results(user_id, tng):
    return models.Result.objects \
        .filter(is_active=True, user_id=hash_(user_id)) \
        .exclude(teacher_n_group__group=tng.group)
