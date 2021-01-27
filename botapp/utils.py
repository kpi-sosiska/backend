import json

from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
from aiogram.utils import deep_linking


def question_keyboard(question, teacher_type, answers=(None, None)):
    def _make_btn(answer_text, row_n, answer_n):
        mark = '✅' if answers[row_n] == answer_n and answer_n is not None else ''
        return types.InlineKeyboardButton(
            mark + answer_text,
            callback_data=json.dumps([question.id, row_n, answer_n])
        )

    buttons = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣'] if question.answer_options == 5 else ['Ні', 'Так']
    buttons = list(enumerate(buttons))
    buttons = [[(None, 'Лектор'), *buttons],
               [(None, 'Практик'), *buttons]] \
        if question.need_two_answers(teacher_type) else \
              [[*buttons]]

    return types.InlineKeyboardMarkup(row_width=len(buttons[0])).add(*[
        _make_btn(answer_text, row_n, answer_n)
        for row_n, answers_row in enumerate(buttons)
        for answer_n, answer_text in answers_row
    ])


def encode_start_teacher(teacher_id, group_id):
    return _encode_deep_link('t', teacher_id, group_id)


def encode_start_group(group_id):
    return _encode_deep_link('g', group_id)


def _encode_deep_link(*args):
    payload = '-'.join(map(str, args))
    payload = deep_linking.encode_payload(payload)
    botname = 'svin_test_bot'
    return f"t.me/{botname}?start={payload}"


def decode_deep_link(payload):
    try:
        payload = deep_linking.decode_payload(payload)
    except Exception:
        return None, None
    args = payload.split('-')
    return args


class DeepLinkFilter(BoundFilter):
    key = 'deep_link'

    def __init__(self, deep_link):
        self.deep_link = deep_link

    async def check(self, message: types.Message):
        payload = message.get_args()
        cmd, *payload = decode_deep_link(payload)
        if cmd == self.deep_link:
            return {'payload': payload}
