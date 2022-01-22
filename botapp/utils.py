import asyncio
import re
from functools import reduce
from hashlib import md5
from html import escape

from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
from aiogram.utils import deep_linking, exceptions
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.markdown import hlink
from mainapp.models import Locale as L, Group

cb_answer = CallbackData("answer", "question", "row", "answer")
cb_help = CallbackData("help", "question")
cb_confirm_group = CallbackData("confirm_group", "group_id")
_lec_btn = types.InlineKeyboardButton(L['2answrs_LECTOR'], callback_data=cb_help.new("2answ"))
_pra_btn = types.InlineKeyboardButton(L['2answrs_PRACTIC'], callback_data=cb_help.new("2answ"))


def question_keyboard(question, teacher_type, answers=(None, None), hide_help=False):
    def _vote_btns(row_num):
        return [
            types.InlineKeyboardButton(
                ('✅' if answers[row_num] == btn_num else '') + btn_text,
                callback_data=cb_answer.new(question.name, row_num, btn_num))
            for btn_num, btn_text in enumerate(buttons)]

    buttons = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣'] if question.answer_options == 5 else ['Ні', 'Так']
    help_btn = types.InlineKeyboardButton("❓", callback_data=cb_help.new(question.name))
    keyboard = types.InlineKeyboardMarkup(row_width=6)

    if question.need_two_answers(teacher_type):
        keyboard.row(_lec_btn, *_vote_btns(0)).row(_pra_btn, *_vote_btns(1))
    else:
        keyboard.row(*_vote_btns(0))

    if not hide_help and question.answer_tip:
        keyboard.insert(help_btn)
    return keyboard


def confirm_group_keyboard(group: Group):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.insert(
        types.InlineKeyboardButton(
            L["confirm_search_group"],
            callback_data=cb_confirm_group.new(group_id=group.id),
        )
    )
    keyboard.insert(
        types.InlineKeyboardButton(
            L["btn_search_group_again"],
            switch_inline_query_current_chat=""
        )
    )
    return keyboard


async def try_send(func, *args, **kwargs):
    for _ in range(5):
        try:
            await func(*args, **kwargs)
            return True
        except exceptions.RetryAfter as ex:
            await asyncio.sleep(ex.timeout + 1)
    return False


def opros_state():
    state = L['opros_state']
    return '0' if state not in ('1', '2', '3', 'posting') else state


async def send_other_teachers_in_group(message: types.Message, group: Group):
    # преподы которых еще нужно пройти отсортированные по кол-ву прохождений
    teachers = group.teacher_need_votes(). \
        exclude(result__user_id=hash_(message.from_user.id), result__is_active=True)

    if not teachers:
        return await message.answer(L['all_prepods_voted'])

    text = L['other_teachers_in_group_text' + opros_state()].format(
        group_name=group.name.upper(),
        teachers=teachers_links(teachers, is_ls=True))
    await message.answer(text)


def teachers_links(tngs, is_ls=False):
    def _link(t):
        return hlink(t.teacher.name, encode_start_teacher(t))

    state = opros_state()
    if is_ls and state == '3':
        state = '2'

    if state == '1':
        f = lambda tng: '• ' + _link(tng)
    elif state == '2':
        _mark = lambda tng: ('❗️ ' if tng.result_need > 0 else '• ')  # todo or tng[0] < 5
        f = lambda tng: _mark(tng) + _link(tng)
    else:
        tngs = [tng for tng in tngs if tng.result_need > 0][:5]
        f = lambda tng: '❗ ' + _link(tng) + f" (ще {tng.result_need} " + \
                        case_by_num(tng.result_need, 'відповідь', 'відповіді', 'відповідей') + ')'

    return '\n'.join(map(f, tngs))


def encode_start_teacher(techer_n_group):
    return _encode_deep_link('t', techer_n_group.id)


def encode_start_group(group_id):
    return _encode_deep_link('g', group_id)


def encode_start_group_user(group_id):
    return _encode_deep_link('gu', group_id)


def _encode_deep_link(*args):
    payload = '|'.join(map(str, args))
    payload = deep_linking.encode_payload(payload)
    return f"t.me/{L['bot_username']}?start={payload}"


def decode_deep_link(payload):
    try:
        payload = deep_linking.decode_payload(payload)
    except Exception:
        return None, None
    args = payload.split('|')
    return args


class DeepLinkFilter(BoundFilter):
    key = 'deep_link'

    def __init__(self, deep_link):
        self.deep_link = deep_link

    async def check(self, message: types.Message):
        payload = message.get_args()
        if not payload:
            return
        cmd, payload = decode_deep_link(payload)
        if cmd == self.deep_link:
            return {'payload': payload}


def hash_(user_id):
    return md5(str(user_id).encode('ascii')).hexdigest()


def case_by_num(num: int, c_1: str, c_2: str, c_3: str) -> str:
    if 11 <= num <= 14:
        return c_3
    if num % 10 == 1:
        return c_1
    if 2 <= num % 10 <= 4:
        return c_2
    return c_3


def censure(text):
    bad_words = L['bad_words'].split(' ')
    t = reduce(lambda res, bad_word: re.sub(bad_word, '*' * len(bad_word), res, flags=re.IGNORECASE), bad_words, text)
    return escape(t, False)
