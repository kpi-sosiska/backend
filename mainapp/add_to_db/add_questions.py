from mainapp.add_to_db._base import reader
from mainapp.models import Question, atomic


with atomic():
    with reader('questions') as csv_reader:
        next(csv_reader)
        for row in csv_reader:
            id_, text, _, angl, lec, pra, two = row
            text, tip = text.split('?')
            text += '?'
            Question(
                id=id_,
                question_text=text,
                answer_tip=tip,
                is_for_eng=bool(angl),
                is_for_lec=bool(lec),
                is_for_pra=bool(pra),
                is_two_answers=bool(two)
            ).save()
