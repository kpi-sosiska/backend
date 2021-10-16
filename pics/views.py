import json

from django.shortcuts import render

from mainapp.models import TEACHER_TYPE, TeacherFacultyResult

default_pic = 'https://cdn.shopify.com/s/files/1/0239/7947/products/hog_e69123f6-2e01-4ddb-9d8f-66bbd9d6d7a4_2048x2048.png?v=1571265926'


def mock(request):
    res = TeacherFacultyResult.objects.get(teacher_id="fffa8bab-52ce-4b4e-90da-73810f47f22b", faculty_id=10106)
    responses = [1, 2, 3]
    answers = {'cheating_l': [3, 5, 4, 6, 0],
               'cheating_p': [3, 5, 4, 6, 0],
               'comfort': [6, 4, 4, 6, 0],
               'conformity': [1, 3, 7, 7, 0],
               'find_out_rating': [4, 11, 3, 3, 0],
               'grading_system': [9, 3, 5, 4, 0],
               'meaningfulness': [5, 4, 5, 2, 0],
               'politeness': [0, 5, 7, 14, 0],
               'punctuality': [2, 4, 8, 13, 0],
               'quality_l': [5, 6, 3, 3, 0],
               'quality_p': [4, 8, 1, 3, 0],
               'questions_available': [1, 3, 5, 11, 0],
               'relevance': [9, 2, 4, 4, 0],
               'self_rating': [4, 9, 3, 3, 0],
               'skills': [1, 3, 8, 10, 0],
               'sufficiency': [6, 8, 3, 4, 0],
               'want_to_continue_l': [13, 0, 0, 0, 0],
               'want_to_continue_p': [10, 0, 0, 0, 0]}

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
