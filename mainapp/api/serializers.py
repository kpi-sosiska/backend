from collections import Counter, defaultdict
from typing import Dict, List

from rest_framework import serializers

from mainapp.models import Faculty, Teacher, University, TeacherFacultyResult


class UniverSerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = ['id', 'name']


class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = ['id', 'name']


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['id', 'name']


class ResultSerializer:
    MIN_VOTES = 0

    @classmethod
    def get_result(cls, teacher, faculty):
        results = TeacherFacultyResult.get_results(teacher, faculty)

        teacher_type, responses = cls.get_responses_and_type(teacher, results)

        if teacher_type is None:
            return None

        answers: Dict[str, List[int]] = defaultdict(list)
        comments = []

        for r in results:
            if r.open_answer_moderate:
                comments.append(r.open_question_answer)

            for a in r.answers.all():
                for qn, answ in a.get_answers().items():
                    answers[qn].append(answ)

        return {
            'teacher_name': teacher.name,
            'teacher_photo': teacher.photo,
            'teacher_type': teacher_type.lower(),
            'responses': responses,
            'answers': answers,
            'comments': comments
        }

    @classmethod
    def get_responses_and_type(cls, teacher, results):
        def get_type():
            if teacher.is_eng:
                return 'ENG' if c['ENG'] > cls.MIN_VOTES else None

            possible_types = [t for t in ('LECTOR', 'PRACTIC')
                              if c[t] + c['LECTOR_PRACTIC'] > cls.MIN_VOTES]
            if len(possible_types) == 2:
                return 'LECTOR_PRACTIC'
            if len(possible_types) == 1:
                return possible_types[0]
            return None

        c = Counter([r.teacher_type for r in results])
        type_ = get_type()
        responses = c['ENG'] if type_ == 'ENG' else c['LECTOR'], c['PRACTIC'], c['LECTOR_PRACTIC']
        return type_, responses
