from django.db import models
from django.db.models import Count, Q
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
        return self.teacherngroup_set.all().annotate(
            results_cnt=Count('result', filter=Q(result__is_active=True))
        ).order_by('results_cnt')

    @classmethod
    def get_groups(cls):
        return cls.objects.values_list('id')

    def link(self):
        from botapp.utils import encode_start_group
        return encode_start_group(self.id)

    def get_results(self):
        from mainapp.models import Result
        return Result.for_teacher(self)

    def __str__(self):
        return f"{self.name} ({self.faculty})"

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"


class Teacher(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    slug = models.SlugField('slug', unique=True)
    name = models.CharField('Имя', max_length=200)
    photo = models.CharField('Ссылка на фото', max_length=500, null=True, blank=True)
    is_eng = models.BooleanField('Это англ?', default=False)

    univer = models.ForeignKey(University, models.CASCADE, verbose_name='Универ')
    groups = models.ManyToManyField(Group, through='TeacherNGroup')

    cathedras = models.TextField("Кафедры", null=True, blank=True)
    lessons = models.TextField("Шо ведет", null=True, blank=True)

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

