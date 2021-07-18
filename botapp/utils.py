import json
from hashlib import md5

from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
from aiogram.utils import deep_linking
from aiogram.utils.markdown import hlink
from mainapp.models import Locale as L


def question_keyboard(question, teacher_type, answers=(None, None)):
    def _make_btn(answer_text, row_n, answer_n):
        mark = '✅' if answers[row_n] == answer_n and answer_n is not None else ''
        return types.InlineKeyboardButton(
            mark + answer_text,
            callback_data=json.dumps([question.id, row_n, answer_n])
        )

    buttons = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣'] if question.answer_options == 5 else ['Ні', 'Так']
    buttons = list(enumerate(buttons))
    buttons = [[(None, L['2answrs_LECTOR']), *buttons],
               [(None, L['2answrs_PRACTIC']), *buttons]] \
        if question.need_two_answers(teacher_type) else \
        [[*buttons]]

    return types.InlineKeyboardMarkup(row_width=len(buttons[0])).add(*[
        _make_btn(answer_text, row_n, answer_n)
        for row_n, answers_row in enumerate(buttons)
        for answer_n, answer_text in answers_row
    ])


def teachers_links(tngs):
    return '\n'.join([
        '• ' + hlink(tng.teacher.name, encode_start_teacher(tng))
        for tng in tngs
    ])


def encode_start_teacher(techer_n_group):
    return _encode_deep_link('t', techer_n_group.id)


def encode_start_group(group_id):
    return _encode_deep_link('g', group_id)


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
