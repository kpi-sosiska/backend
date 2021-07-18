from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .utils import ModelAdminByUniver, RelatedFieldListFilterByUniver, IsFinishedListFilter, export_groups, short_fio
from mainapp.models import Locale, Question, Teacher, Result, ResultAnswers, Group, TeacherNGroup, Faculty, CustomUser, \
    University


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password', 'univer')}),
        (_('Permissions'), {'fields': ('is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('username', 'univer', 'is_superuser')
    list_filter = ('univer', )
    search_fields = ('username', 'univer')
    ordering = ('-is_superuser', 'univer')


@admin.register(Locale)
class LocaleAdmin(admin.ModelAdmin):
    empty_value_display = 'Не заполнено'
    list_display = ('key', 'value')
    list_editable = ('value',)


@admin.register(Group)
class GroupAdmin(ModelAdminByUniver):
    # todo override get_preserved_filters to set faculty from req.user

    @admin.display(description='Ссылка на розклад')
    def rozklad_link(self, obj):
        return mark_safe(f'<a href="http://rozklad.kpi.ua/Schedules/ViewSchedule.aspx?g={obj.id}">{obj.id}</a>')

    @admin.display(description='Преподы')
    def teacher_list(self, obj):
        teachers = obj.teachers.all().values_list('name', flat=True).order_by('name').distinct()
        return '; '.join([short_fio(t) for t in teachers])

    class TeacherInline(admin.TabularInline):
        autocomplete_fields = ('teacher',)
        model = TeacherNGroup
        extra = 1

    univer_field_path = "faculty__univer"
    readonly_fields = ('rozklad_link', 'link')
    autocomplete_fields = ('faculty',)
    list_display = ('name', 'faculty', 'teacher_list')
    list_filter = (
        ('faculty', RelatedFieldListFilterByUniver),
        ('faculty__univer', admin.RelatedOnlyFieldListFilter),
    )
    search_fields = ('name',)
    actions = (export_groups, )
    inlines = (TeacherInline, )
    ordering = ('name',)


@admin.register(Teacher)
class TeacherAdmin(ModelAdminByUniver):
    class GroupInline(admin.TabularInline):
        autocomplete_fields = ('group', )
        model = TeacherNGroup
        extra = 1

    @admin.display(description='Факультеты')
    def faculties(self, obj):
        return list(Faculty.objects.filter(group__teachers__id=obj.id).distinct())

    @admin.display(description='Ссылка на розклад')
    def rozklad_link(self, obj):
        return mark_safe(f'<a href="http://rozklad.kpi.ua/Schedules/ViewSchedule.aspx?v={obj.id}">{obj.id}</a>')

    @admin.display(description='Фото')
    def photo_img(self, obj):
        return mark_safe(f'<img src="{obj.photo}" width="50px">') if obj.photo else None

    univer_field_path = "univer"
    readonly_fields = ('rozklad_link',)
    list_display = ('name', 'lessons', 'cathedras', 'faculties', 'photo_img')
    list_editable = ('lessons',)
    list_filter = (
        ('groups__faculty', RelatedFieldListFilterByUniver),
        ('univer', admin.RelatedOnlyFieldListFilter),
        ("photo", admin.EmptyFieldListFilter)
    )
    search_fields = ('name',)
    inlines = (GroupInline, )
    ordering = ('name', )


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ('name', )


@admin.register(Faculty)
class FacultyAdmin(ModelAdminByUniver):
    univer_field_path = "univer"
    search_fields = ('name', )
    list_display = ('name', 'univer', 'poll_result_link')
    list_editable = ('poll_result_link',)
    list_filter = ('univer', )


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'answer_tip', 'is_for_eng', 'is_for_lec', 'is_for_pra', 'is_two_answers')
    list_editable = ('answer_tip',)


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    class AnswerInline(admin.TabularInline):
        model = ResultAnswers
        extra = 0

    @admin.display(description='Препод')
    def teacher(self, obj):
        return obj.teacher_n_group.teacher

    @admin.display(description='Группа')
    def group(self, obj):
        return obj.teacher_n_group.group

    @admin.display(description='Закончил опрос', boolean=True)
    def is_finished(self, obj):
        return obj.time_finish is not None

    list_display = ('user_id', 'teacher', 'group', 'teacher_type', 'is_finished')
    list_filter = (
        ('teacher_n_group__teacher', admin.RelatedOnlyFieldListFilter),
        ('teacher_n_group__group', admin.RelatedOnlyFieldListFilter),
        IsFinishedListFilter
    )
    readonly_fields = ('teacher_n_group', 'time_start', 'time_finish')
    inlines = (AnswerInline, )
