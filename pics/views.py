import json

from django.shortcuts import render

from mainapp.models import TEACHER_TYPE, TeacherFacultyResult

default_pic = 'https://cdn.shopify.com/s/files/1/0239/7947/products/hog_e69123f6-2e01-4ddb-9d8f-66bbd9d6d7a4_2048x2048.png?v=1571265926'


def main(request, teacher, faculty):
    res = TeacherFacultyResult.objects.get(teacher_id=teacher, faculty_id=faculty)
    responses, answers = res.answers()

    # зацени шо есть в answers
    from pprint import pprint
    pprint(answers)

    # значения для темплейтов можно попить, а все шо останется пусть процессится джусиком
    meaningfulness = my_cool_average(answers.pop("meaningfulness"))
    skills = my_cool_average(answers.pop("skills"))

    context = {
        'teacher_name': res.teacher.name,
        'teacher_photo': res.teacher.photo,

        'teacher_type': res.teacher_type.lower(),
        'teacher_type_text': TEACHER_TYPE[res.teacher_type],

        'meaningfulness': meaningfulness,
        'skills': skills,

        'responses': responses,

        'json': json.dumps({
            "type": res.teacher_type.lower(),
            "answers": answers
        })
    }

    return render(request, context['teacher_type'] + '.html', context)


def my_cool_average(kek):
    return sum((i + 1) * v for i, v in enumerate(kek))
