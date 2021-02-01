from django.db import models, transaction
from django.db.models import Q

atomic = transaction.atomic


TEACHER_TYPE = {
    'LECTOR': 'Лектор',
    'PRACTIC': 'Практик',
    'LECTOR_PRACTIC': 'Лектор и практик',
    'ENG': 'Английский',
}


class Teacher(models.Model):
    name = models.CharField('Имя', max_length=200)
    photo = models.CharField('Ссылка на фото', max_length=100, null=True, blank=True)
    is_eng = models.BooleanField('Это англ?', default=False)

    groups = models.ManyToManyField('Group', through='TeacherNGroup')

    @classmethod
    def add(cls, id_, name, type_, group):
        teacher = cls(id=id_, name=name, is_eng=type_ == 'ENG')
        teacher.save()
        group.teachers.add(teacher)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Препод"
        verbose_name_plural = "Преподы"


class Faculty(models.Model):
    name = models.CharField('Факультет', max_length=10, null=True)
    poll_result_link = models.CharField('Ссылка на результаты опроса', max_length=100, null=True)

    def __str__(self):
        return self.name


class Group(models.Model):
    name = models.CharField('Код', max_length=20)
    faculty = models.ForeignKey(Faculty, models.CASCADE, verbose_name='Факультет')
    teachers = models.ManyToManyField(Teacher, through='TeacherNGroup')

    @classmethod
    def add(cls, id_, name, faculty):
        group = cls(id=id_, name=name, faculty=faculty)
        group.save()
        return group

    @classmethod
    def get_groups(cls):
        return cls.objects.values_list('id')

    def link(self):
        from botapp.utils import encode_start_group
        return encode_start_group(self.id)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"


class TeacherNGroup(models.Model):
    teacher = models.ForeignKey(Teacher, models.CASCADE, verbose_name='Препод')
    group = models.ForeignKey(Group, models.CASCADE, verbose_name='Группа')

    def __str__(self):
        return f"{self.teacher} в {self.group}"

    def link(self):
        from botapp.utils import encode_start_teacher
        return encode_start_teacher(self.teacher_id, self.group_id)

    class Meta:
        unique_together = ('teacher', 'group')
        verbose_name = "Препод+Группа"
        verbose_name_plural = "Преподы+Группы"


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
    user_id = models.PositiveIntegerField('ID ответившего')
    teacher_n_group = models.ForeignKey(TeacherNGroup, models.CASCADE, verbose_name='Препод и группа')
    teacher_type = models.CharField('Тип опросника', max_length=20,
                                    choices=TEACHER_TYPE.items(), default=list(TEACHER_TYPE)[0])

    open_question_answer = models.TextField('Ответ свободного микрофона', null=True, blank=True)

    date = models.DateTimeField('Дата прохождения', auto_now_add=True)

    @classmethod
    def add(cls, user_id, teacher_n_group, teacher_type, open_question_answer, other_answers):
        with atomic():
            result, _ = cls.objects.update_or_create(
                user_id=user_id, teacher_n_group=teacher_n_group, defaults=dict(
                    teacher_type=teacher_type, open_question_answer=open_question_answer
                ))
            for question_id, answers in other_answers.items():
                if len(answers) == 1:
                    answers.append(None)
                ResultAnswers.objects.update_or_create(result=result, question_id=question_id, defaults=dict(
                                                       answer_1=answers[0], answer_2=answers[1]))

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


#


class Locale(models.Model):
    key = models.CharField(max_length=50, unique=True)
    value = models.TextField(null=True)

    def __class_getitem__(cls, item) -> str:
        obj, _ = cls.objects.get_or_create(key=item)
        return obj.value or obj.key

    def __str__(self):
        return f"{self.key} -> {self.value or 'Не заполнено'}"

    class Meta:
        verbose_name = "Текст"
        verbose_name_plural = "Текста"
