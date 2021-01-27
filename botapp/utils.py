import json

from aiogram import types
from aiogram.utils.markdown import hlink

from mainapp.models import Locale as L
from mainapp import models


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


def make_group_teachers_text(group_name):
    group = models.Group.objects.get(name__icontains=group_name)
    teachers = [
        hlink('• ' + t.name, encode_deep_link(t.id, group.id))
        for t in group.teachers.all()
    ]
    return L['group_teachers_text'].format(
        group_name=group.name.upper(), results_link=group.faculty.poll_result_link, teachers='\n'.join(teachers)
    )


def encode_deep_link(teacher_id, group_id):
    botname = 'svin_test_bot'
    return f"t.me/{botname}?start={teacher_id}-{group_id}"


def decode_deep_link(args):
    # decode
    teacher, faculty = args.split('-')
    return int(teacher), int(faculty)
