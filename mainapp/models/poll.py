from collections import Counter, defaultdict
from contextlib import suppress
from typing import Dict, List

from django.db import models, transaction, IntegrityError
from django.db.models import Q
from django.utils import timezone

from mainapp.models.teachers import Faculty, TEACHER_TYPE, Teacher, TeacherNGroup


class Question(models.Model):
    name = models.CharField('Название', max_length=20, primary_key=True)
    order = models.PositiveIntegerField('№', default=0, blank=False, null=False)

    question_text = models.TextField('Вопрос')
    answer_tip = models.TextField('Примечания', blank=True, null=True)

    answer_options = models.PositiveSmallIntegerField('1-5 или нет/да', choices=((5, '1-5'), (2, 'Нет/Да')), default=5)

    is_for_eng = models.BooleanField('для Англ', default=False)
    is_for_lec = models.BooleanField('для Лектора', default=False)
    is_for_pra = models.BooleanField('для Практика', default=False)
    is_two_answers = models.BooleanField('Разделять ответы для лектора и практика', default=False)

    @classmethod
    def get_by_type(cls, type_):
        query_by_type_ = {
            'ENG': Q(is_for_eng=True),
            'LECTOR': Q(is_for_lec=True),
            'PRACTIC': Q(is_for_pra=True),
            'LECTOR_PRACTIC': Q(is_for_lec=True) | Q(is_for_pra=True)
        }
        return cls.objects.filter(query_by_type_[type_])

    def __str__(self):
        return self.question_text[:100]

    def need_two_answers(self, teacher_type):
        return teacher_type == 'LECTOR_PRACTIC' and self.is_for_lec and self.is_for_pra and self.is_two_answers

    class Meta:
        ordering = ['order']
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"


class Result(models.Model):
    user_id = models.CharField('ID ответившего', max_length=32)
    teacher_n_group = models.ForeignKey(TeacherNGroup, models.CASCADE, verbose_name='Препод и группа')
    teacher_type = models.CharField('Тип опросника', max_length=20, null=True, choices=TEACHER_TYPE.items())

    open_question_answer = models.TextField('Ответ свободного микрофона', null=True, blank=True)
    open_answer_moderate = models.BooleanField('Комментарий допущен?', null=True)

    is_active = models.BooleanField("Актуальный результат", default=False,
                                    help_text="Последний законченный результат этого юзера по этому преподу")
    time_start = models.DateTimeField('Время начала прохождения', auto_now_add=True)
    time_finish = models.DateTimeField('Время окончания прохождения', null=True, default=None)

    def finish(self, teacher_type, open_question_answer, other_answers):
        with transaction.atomic():
            Result.objects.filter(user_id=self.user_id, teacher_n_group=self.teacher_n_group).update(is_active=False)
            self.teacher_type = teacher_type
            self.open_question_answer = open_question_answer
            self.is_active = True
            self.time_finish = timezone.now()
            self.save()

            for question_id, answers in other_answers.items():
                if len(answers) == 1:
                    answers.append(None)
                ResultAnswers.objects.create(result=self, question_id=question_id,
                                             answer_1=answers[0], answer_2=answers[1])

    def __str__(self):
        return f"{self.teacher_n_group} {self.get_teacher_type_display()}"

    class Meta:
        verbose_name = "Результат опроса"
        verbose_name_plural = "Результаты опроса"


class ResultAnswers(models.Model):
    result = models.ForeignKey(Result, models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, models.CASCADE, verbose_name='Вопрос')
    answer_1 = models.PositiveSmallIntegerField('Ответ')
    answer_2 = models.PositiveSmallIntegerField('Еще ответ', null=True, blank=True)

    def get_answers(self, teacher_type):
        gen = self.question.name
        lec, prac = gen + '_l', gen + '_p'

        if self.question.is_two_answers and teacher_type == 'LECTOR_PRACTIC':
            return {lec: self.answer_1, prac: self.answer_2}
        return {gen: self.answer_1}

    def __str__(self):
        return ''

    class Meta:
        verbose_name = "Ответ на вопрос"
        verbose_name_plural = "Ответы на вопросы"


# Cached results with known teacher_type and for different faculties

class TeacherFacultyResult(models.Model):
    teacher = models.ForeignKey(Teacher, models.CASCADE, verbose_name='Препод')
    faculty = models.ForeignKey(Faculty, models.CASCADE, verbose_name='Факультет')
    teacher_type = models.CharField('Тип препода', max_length=20, choices=TEACHER_TYPE.items())
    message_id = models.IntegerField('Айди сообщения на канале (если запощено)', null=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.teacher_type:
            self.teacher_type = self.calculate_type()

    @classmethod
    def calculate_all(cls):
        TeacherFacultyResult.objects.all().delete()
        for t, f in Result.objects.all().values_list('teacher_n_group__teacher',
                                                     'teacher_n_group__group__faculty').distinct():
            with suppress(ValueError, IntegrityError):
                TeacherFacultyResult(teacher_id=t, faculty_id=f).save()

    def tg_link(self):
        return self.faculty.poll_result_link.removeprefix('@') + str(self.message_id)

    def answers(self):
        def format_answers(qn, a_):
            c_ = Counter(a_)
            r = 2 if qn.startswith('want_to_continue') else 5
            return [c_[i] for i in range(r)]

        results = self.results()
        c = Counter([r.teacher_type for r in results])
        responses = c['ENG'] if self.teacher_type == 'ENG' else c['LECTOR'], c['PRACTIC'], c['LECTOR_PRACTIC']

        answers: Dict[str, List[int]] = defaultdict(list)
        for r in results:
            for a in r.answers.all():
                for qn, answ in a.get_answers(self.teacher_type).items():
                    answers[qn].append(answ)

        answers_c = {qn: format_answers(qn, a) for qn, a in answers.items()}
        return responses, answers_c

    def results(self):
        return Result.objects.filter(
            is_active=True,
            teacher_n_group__teacher=self.teacher,
            teacher_n_group__group__faculty=self.faculty
        ).prefetch_related('answers__question')

    def calculate_type(self):
        min_votes = self.faculty.votes_threshold
        c = Counter([r.teacher_type for r in self.results()])
        if self.teacher.is_eng:
            if c['ENG'] > min_votes:
                return 'ENG'
        else:
            possible_types = [t for t in ('LECTOR', 'PRACTIC') if c[t] + c['LECTOR_PRACTIC'] > min_votes]
            if len(possible_types) == 2:
                return 'LECTOR_PRACTIC'
            elif len(possible_types) == 1:
                return possible_types[0]

        raise ValueError("Too few responses")

    def __str__(self):
        return f"{self.teacher} в {self.faculty}"

    class Meta:
        verbose_name = "Результат препода на факультете"
        unique_together = ('teacher', 'faculty')

#  защита от спама
# 1. время заполнения анкеты
# 2. у препода много похожих ответов от людей, которые проходили только этого препода
# 3. у голосовавшего все ответы похожи
#
