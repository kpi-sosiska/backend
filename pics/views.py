import json

from django.shortcuts import render

from mainapp.models import TEACHER_TYPE, TeacherFacultyResult


def mock(request, t):
    if t == 'eng':
        context = {'teacher_name': 'Чіжова Наталія Володимирівна', 'teacher_photo': 'https://kamgs3.kpi.ua/wp-content/uploads/2021/06/%D0%A7%D1%96%D0%B6%D0%BE%D0%B2%D0%B0-760x717.jpg', 'teacher_type': 'eng', 'teacher_type_text': 'Английский', 'json': '{"type": "eng", "answers": {"questions_available": [0, 0, 5, 5, 0], "find_out_rating": [0, 0, 2, 10, 0], "relevance": [1, 4, 4, 3, 0], "sufficiency": [0, 2, 2, 8, 0], "comfort": [0, 1, 4, 7, 0], "skills": [0, 1, 7, 4, 0], "meaningfulness": [1, 1, 6, 4, 0], "politeness": [0, 0, 1, 11, 0], "punctuality": [0, 0, 1, 11, 0], "grading_system": [0, 1, 4, 7, 0], "cheating": [2, 7, 1, 1, 0], "quality": [0, 5, 5, 1, 0], "self_rating": [0, 5, 2, 5, 0], "want_to_continue": [12, 0, 0, 0, 0]}, "responses": [12, 0, 0]}'}
    elif t == 'lector':
        context = {'teacher_name': 'Пап Ірина Вікторівна', 'teacher_photo': None, 'teacher_type': 'lector', 'teacher_type_text': 'Лектор', 'json': '{"type": "lector", "answers": {"questions_available": [0, 0, 1, 10, 0], "find_out_rating": [0, 1, 6, 4, 0], "relevance": [0, 1, 1, 9, 0], "sufficiency": [0, 2, 2, 7, 0], "quality": [0, 1, 2, 2, 0], "conformity": [1, 3, 0, 7, 0], "skills": [0, 1, 1, 9, 0], "meaningfulness": [0, 1, 2, 8, 0], "politeness": [0, 0, 1, 10, 0], "punctuality": [0, 1, 2, 8, 0], "grading_system": [0, 2, 1, 8, 0], "cheating": [1, 2, 2, 0, 0], "self_rating": [0, 4, 3, 4, 0], "want_to_continue": [3, 0, 1, 1, 0], "quality_l": [0, 0, 1, 5, 0], "quality_p": [0, 0, 2, 4, 0], "comfort": [0, 0, 1, 5, 0], "cheating_l": [1, 2, 2, 1, 0], "cheating_p": [0, 2, 2, 1, 0], "want_to_continue_l": [5, 0, 0, 1, 0], "want_to_continue_p": [5, 0, 0, 1, 0]}, "responses": [5, 0, 6]}'}
    elif t == 'practic':
        context = {'teacher_name': 'Вовк Євгеній Андрійович', 'teacher_photo': 'https://hatomist.pw/images/314/%D0%92%D0%BE%D0%B2%D0%BA%20%D0%95%D0%B2%D0%B3%D0%B5%D0%BD%D0%B8%D0%B8%CC%86.jpeg', 'teacher_type': 'practic', 'teacher_type_text': 'Практик', 'json': '{"type": "practic", "answers": {"find_out_rating": [0, 2, 10, 22, 0], "relevance": [0, 1, 3, 30, 0], "comfort": [5, 7, 6, 14, 0], "skills": [0, 0, 2, 32, 0], "meaningfulness": [1, 3, 3, 27, 0], "politeness": [0, 5, 7, 22, 0], "punctuality": [1, 7, 11, 14, 0], "grading_system": [4, 2, 5, 20, 0], "cheating": [0, 0, 0, 33, 0], "quality": [2, 4, 6, 20, 0], "self_rating": [0, 1, 6, 25, 0], "want_to_continue": [30, 0, 0, 0, 0]}, "responses": [0, 34, 0]}'}
    elif t == 'lector_practic':
        context = {'teacher_name': 'Герасимчук Валентина Андріївна', 'teacher_photo': 'https://feedbackglobal.org/wp-content/uploads/2013/09/piglet-1326946_1920-1024x681.jpg', 'teacher_type': 'lector_practic', 'teacher_type_text': 'Лектор и практик', 'json': '{"type": "lector_practic", "answers": {"questions_available": [1, 3, 5, 11, 0], "find_out_rating": [4, 11, 3, 3, 0], "relevance": [9, 2, 4, 4, 0], "sufficiency": [6, 8, 3, 4, 0], "comfort": [6, 4, 4, 6, 0], "conformity": [1, 3, 7, 7, 0], "skills": [1, 3, 8, 10, 0], "meaningfulness": [5, 4, 5, 2, 0], "politeness": [0, 5, 7, 14, 0], "punctuality": [2, 4, 8, 13, 0], "grading_system": [9, 3, 5, 4, 0], "cheating_l": [3, 4, 4, 5, 0], "cheating_p": [3, 5, 4, 5, 0], "quality_l": [5, 6, 2, 2, 0], "quality_p": [4, 8, 1, 3, 0], "self_rating": [4, 9, 3, 3, 0], "want_to_continue_l": [11, 0, 0, 0, 0], "want_to_continue_p": [10, 0, 0, 0, 0], "cheating": [0, 1, 0, 2, 0], "quality": [0, 0, 1, 1, 0], "want_to_continue": [2, 0, 0, 0, 0]}, "responses": [2, 1, 26]}'}
    else:
        raise ValueError("Wrong teacher type")

    return render(request, t + '.html', context)


def main(request, teacher, faculty):
    res = TeacherFacultyResult.objects.get(teacher_id=teacher, faculty_id=faculty)
    responses, answers = res.answers()

    context = {
        'teacher_name': res.teacher.name,
        'teacher_photo': res.teacher.photo,

        'teacher_type': res.teacher_type.lower(),
        'teacher_type_text': TEACHER_TYPE[res.teacher_type],

        'json': json.dumps({
            "type": res.teacher_type.lower(),
            "answers": answers,
            'responses': responses,
        })
    }

    return render(request, context['teacher_type'] + '.html', context)
