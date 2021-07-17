from django.db import models, transaction
from django.db.models import Q
from django.utils import timezone

from mainapp.models.teachers import TEACHER_TYPE, TeacherNGroup


class Question(models.Model):
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
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"


class Result(models.Model):
    user_id = models.CharField('ID ответившего', max_length=32)
    teacher_n_group = models.ForeignKey(TeacherNGroup, models.CASCADE, verbose_name='Препод и группа')
    teacher_type = models.CharField('Тип опросника', max_length=20, null=True, choices=TEACHER_TYPE.items())

    open_question_answer = models.TextField('Ответ свободного микрофона', null=True, blank=True)

    time_start = models.DateTimeField('Время начала прохождения', auto_now_add=True)
    time_finish = models.DateTimeField('Время окончания прохождения', null=True, default=None)

    @classmethod
    def filter_finished(cls):
        return cls.objects.filter(time_finish__isnull=False)

    @classmethod
    def add(cls, user_id, teacher_n_group, teacher_type, open_question_answer, other_answers):
        with transaction.atomic():
            result, _ = cls.objects.update_or_create(
                user_id=user_id, teacher_n_group=teacher_n_group,
                defaults=dict(
                    time_finish=timezone.now(),
                    teacher_type=teacher_type,
                    open_question_answer=open_question_answer
                ))

            ResultAnswers.objects.filter(result=result).delete()  # удалить старые результаты (если это перепрохождение)
            for question_id, answers in other_answers.items():
                if len(answers) == 1:
                    answers.append(None)
                ResultAnswers.objects.create(result=result, question_id=question_id,
                                             answer_1=answers[0], answer_2=answers[1])

    def __str__(self):
        return f"{self.teacher_n_group} {self.get_teacher_type_display()}"

    class Meta:
        unique_together = ('user_id', 'teacher_n_group')
        verbose_name = "Результат опроса"
        verbose_name_plural = "Результаты опроса"


class ResultAnswers(models.Model):
    result = models.ForeignKey(Result, models.CASCADE)
    question = models.ForeignKey(Question, models.CASCADE, verbose_name='Вопрос')
    answer_1 = models.PositiveSmallIntegerField('Ответ')
    answer_2 = models.PositiveSmallIntegerField('Еще ответ', null=True, blank=True)

    def __str__(self):
        return ''

    class Meta:
        verbose_name = "Ответ на вопрос"
        verbose_name_plural = "Ответы на вопросы"

