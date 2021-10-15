import json

from django.shortcuts import render

from mainapp.models import TEACHER_TYPE

default_pic = 'https://cdn.shopify.com/s/files/1/0239/7947/products/hog_e69123f6-2e01-4ddb-9d8f-66bbd9d6d7a4_2048x2048.png?v=1571265926'


# todo test view

def main(request):
    teacher_type = 'LECTOR_PRACTIC'
    context = {
        'teacher_name': 'Головач Елена Совухина',
        'teacher_photo': "https://hatomist.pw/images/314/%D0%91%D0%BB%D0%B0%D0%B6%D1%96%D1%94%D0%B2%D1%81%D1%8C%D0%BA%D0%B0%20%D0%86%D1%80%D0%B8%D0%BD%D0%B0.jpeg" or default_pic,

        'teacher_type': teacher_type.lower(),
        'teacher_type_text': TEACHER_TYPE[teacher_type],

        'want_to_continue': 75,
        'want_to_continue_p': 75,

        'meaningfulness': 4.2,
        'grading_system': 3.1,

        'cheating': 1.2,
        'skills': 5,

        'responses': [5, 4, 42],

        'json': json.dumps(
            {"type": teacher_type.lower(),
             "radial": {
                 "politeness": 4.526315789473684,

                 "sufficiency": 4.636363636363637,
                 "questions_available": 4.2727272727272725,

                 "objectivity": 4.545454545454546,
                 "punctuality": 4.363636363636363,
                 "cheating": 4.636363636363637,
                 "timely_informing": 4.545454545454546,

                 "conformity": 4.363636363636363,

                 "timely_informing *": 4.4411764705882355,
                 "punctuality *": 4.5588235294117645,
                 "cheating *": 4.147058823529412,
                 "objectivity *": 4.5,

                 "comfort": 4.294117647058823,
                 "relevance": 4,
             },
             "barChart": {"quality": [1, 0, 0, 1, 9],
                          "quality *": [1, 0, 0, 1, 9],
                          "self_rating": [1, 0, 0, 1, 9],
                          }
             })
    }

    return render(request, context['teacher_type'] + '.html', context)
