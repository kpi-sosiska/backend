import json
from collections import Counter, defaultdict
from typing import Dict, List
from django.http import HttpResponse

from mainapp.models import Result, TEACHER_TYPE, TeacherFacultyResult


def tr(f, t):
    rs = TeacherFacultyResult.get_results(t, f)

    resp_count = Counter([r.teacher_type for r in rs])
    teacher_type = get_type(resp_count)

    if teacher_type is None:
        return None

    responses = resp_count['ENG'] if teacher_type == 'ENG' else \
        resp_count['LECTOR'], resp_count['PRACTIC'], resp_count['LECTOR_PRACTIC']

    answers: Dict[str, List[int]] = defaultdict(list)
    comments = []

    for r in rs:
        if r.open_answer_moderate:
            comments.append(r.open_question_answer)

        for a in r.answers.all():
            for qn, answ in a.get_answers().items():
                answers[qn].append(answ)

    return json.dumps({
        'teacher_name': t.name,
        'teacher_photo': t.photo,

        'teacher_type': teacher_type.lower(),
        'teacher_type_text': TEACHER_TYPE[teacher_type],

        'responses': responses,
        'answers': answers,
        'comments': comments
    })


min_votes = 0


def get_type(c):
    possible_types = []
    if c['ENG'] > min_votes:
        possible_types.append('ENG')

    for t in ('LECTOR', 'PRACTIC'):
        if c[t] + c['LECTOR_PRACTIC'] > min_votes:
            possible_types.append(t)
    if len(possible_types) == 2:
        return 'LECTOR_PRACTIC'
    if len(possible_types) == 1:
        return possible_types[0]
    return None


def main(request):
    r = Result.objects.get(id=12)
    rs = tr(r.teacher_n_group.group.faculty, r.teacher_n_group.teacher)

    return HttpResponse(rs)
