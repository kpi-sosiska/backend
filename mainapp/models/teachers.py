from django.db import models
from django.db.models import Count, Q, F, Subquery
from django.utils.text import slugify

from transliterate import translit


TEACHER_TYPE = {
    'LECTOR': 'Лектор',
    'PRACTIC': 'Практик',
    'LECTOR_PRACTIC': 'Лектор и практик',
    'ENG': 'Английский',
}


class University(models.Model):
    name = models.CharField('Короткое название', max_length=10)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Универ"
        verbose_name_plural = "Универы"


class Faculty(models.Model):
    name = models.CharField('Факультет', max_length=10, null=True)
    univer = models.ForeignKey(University, models.CASCADE, verbose_name='Универ')
    votes_threshold = models.SmallIntegerField('Минимальное количество голосов для препода', default=10)
    poll_result_link = models.CharField('Ссылка на результаты опроса', max_length=100, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Факультет"
        verbose_name_plural = "Факультеты"


class Group(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    name = models.CharField('Код', max_length=20)
    faculty = models.ForeignKey(Faculty, models.CASCADE, verbose_name='Факультет', null=True, blank=True)
    teachers = models.ManyToManyField('Teacher', through='TeacherNGroup')

    def teacher_need_votes(self):
        # todo пиздец оно по другому никак не хотело правильно считать
        return self.teacherngroup_set.all().annotate(
            results_cnt=Count('teacher__teacherngroup__result',
                              filter=Q(teacher__teacherngroup__result__is_active=True) &
                                     Q(teacher__teacherngroup__result__teacher_n_group__teacher_id=F('teacher_id')) &
                                     Q(teacher__teacherngroup__result__teacher_n_group__group__faculty_id=self.faculty_id)
                              ),
            result_need=F('group__faculty__votes_threshold') - F('results_cnt'),
        ).order_by('results_cnt')

    def link(self):
        from botapp.utils import encode_start_group
        return encode_start_group(self.id)

    @property
    def rozklad_link(self):
        return "http://rozklad.kpi.ua/Schedules/ViewSchedule.aspx?g=" + self.id

    def __str__(self):
        return f"{self.name} ({self.faculty})"

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"


class Teacher(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    slug = models.SlugField('slug', unique=True, null=True)
    name = models.CharField('Имя', max_length=200)
    photo = models.CharField('Ссылка на фото', max_length=500, null=True, blank=True)
    is_eng = models.BooleanField('Это англ?', default=False)

    univer = models.ForeignKey(University, models.CASCADE, verbose_name='Универ')
    groups = models.ManyToManyField(Group, through='TeacherNGroup')

    cathedras = models.TextField("Кафедры", null=True, blank=True)
    lessons = models.TextField("Шо ведет", null=True, blank=True)

    def get_faculties(self):
        return Faculty.objects.filter(group__teacher=self)

    def get_comments(self, faculty):
        from mainapp.models import Result
        return Result.objects.filter(is_active=True, teacher_n_group__teacher=self, teacher_n_group__group__faculty_id=faculty,
                                     open_answer_moderate=True).values_list('open_question_answer')

    def create_slug(self):
        return slugify(translit(self.short_fio(), 'uk', reversed=True) + self.id[-13:-7])

    def short_fio(self):
        if '.' in self.name:
            return self.name
        try:
            p = self.name.split(' ')
            return f"{p[0]} {p[1][0]}. {p[2][0]}"
        except:
            return self.name

    def save(self, *args, **kwargs):
        self.slug = self.create_slug()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Препод"
        verbose_name_plural = "Преподы"


class TeacherNGroup(models.Model):
    teacher = models.ForeignKey(Teacher, models.CASCADE, verbose_name='Препод')
    group = models.ForeignKey(Group, models.CASCADE, verbose_name='Группа')

    def __str__(self):
        return f"{self.teacher} в {self.group}"

    def link(self):
        from botapp.utils import encode_start_teacher
        return encode_start_teacher(self.id)

    class Meta:
        unique_together = ('teacher', 'group')
        verbose_name = "Препод+Группа"
        verbose_name_plural = "Преподы+Группы"
