import json
import logging
import uuid
from base64 import urlsafe_b64decode, urlsafe_b64encode

from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
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


def teachers_links(teachers, group_id):
    return '\n'.join([
        '• ' + hlink(t.name, encode_start_teacher(t.id, group_id))
        for t in teachers
    ])


def encode_start_teacher(teacher_id, group_id):
    return _encode_deep_link('t', teacher_id, group_id)


def encode_start_group(group_id):
    return _encode_deep_link('g', group_id)


# deeplink payload max is 64 bytes
# cmd + | + uuid + | + uuid = 1 + 1 + 36 + 1 + 36 bytes = дохуя
# so use bytes


def _encode_deep_link(*args):
    type_, *uuids = args
    payload = b"".join([type_.encode('utf-8')] + [uuid.UUID(u).bytes for u in uuids])
    payload = urlsafe_b64encode(payload).decode().replace("=", "")
    return f"t.me/{L['bot_username']}?start={payload}"


def decode_deep_link(payload_text):
    payload_text += "=" * (4 - len(payload_text) % 4)
    try:
        payload = urlsafe_b64decode(payload_text)
        type_, *uuids = payload
        uuids = [
            str(uuid.UUID(bytes=bytes(uuids[i:i + 16])))
            for i in range(0, len(uuids), 16)
        ]
        return bytes([type_]).decode(), uuids
    except Exception:
        logging.exception("wrong payload" + payload_text)
        return None, []


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
