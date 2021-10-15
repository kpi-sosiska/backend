from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import Exists, OuterRef, Q
from django.forms import Textarea
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.db import models

from .utils import ModelAdminByUniver, RelatedFieldListFilterByUniver, export_groups, BooleanFilterBase
from mainapp.models import Locale, Question, Teacher, Result, ResultAnswers, Group, TeacherNGroup, Faculty, CustomUser, \
    University, TeacherFacultyResult


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password', 'univer')}),
        (_('Permissions'), {'fields': ('is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = ((None, {
        'classes': ('wide',),
        'fields': ('username', 'password1', 'password2', 'univer'),
    }),)
    list_display = ('username', 'univer', 'is_superuser')
    list_filter = ('univer',)
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
        if obj.faculty.univer_id == 1:
            return mark_safe(f'<a href="http://rozklad.kpi.ua/Schedules/ViewSchedule.aspx?g={obj.id}">{obj.id}</a>')

    @admin.display(description='Преподы')
    def teacher_list(self, obj):
        return '; '.join([t.short_fio() for t in obj.teachers.all().distinct()])

    @admin.display(description='Кол-во голосов')
    def votes_count(self, obj):
        all_ = Result.objects.filter(teacher_n_group__group=obj, is_active=True).values('user_id')
        return f"{all_.count()} ({all_.distinct().count()})"

    class TeacherInline(admin.TabularInline):
        autocomplete_fields = ('teacher',)
        model = TeacherNGroup
        extra = 1

    univer_field_path = "faculty__univer"
    readonly_fields = ('rozklad_link', 'link')
    autocomplete_fields = ('faculty',)
    list_display = ('name', 'faculty', 'teacher_list', 'votes_count')
    list_filter = (
        ('faculty', RelatedFieldListFilterByUniver),
        ('faculty__univer', admin.RelatedOnlyFieldListFilter),
    )
    search_fields = ('name',)
    actions = (export_groups,)
    inlines = (TeacherInline,)
    ordering = ('name',)


@admin.register(Teacher)
class TeacherAdmin(ModelAdminByUniver):
    class GroupInline(admin.TabularInline):
        autocomplete_fields = ('group',)
        model = TeacherNGroup
        extra = 1

    @admin.display(description='Факультеты')
    def faculties(self, obj):
        return list(obj.get_faculties().distinct())

    @admin.display(description='Ссылка на розклад')
    def rozklad_link(self, obj):
        if obj.univer_id == 1:
            return mark_safe(f'<a href="http://rozklad.kpi.ua/Schedules/ViewSchedule.aspx?v={obj.id}">{obj.id}</a>')

    @admin.display(description='Фото')
    def photo_img(self, obj):
        if obj.photo:
            return mark_safe(f'<img src="{obj.photo}" width="50px">')

    @admin.display(description='Кол-во голосов')
    def votes_count(self, obj):
        return Result.objects.filter(teacher_n_group__teacher=obj, is_active=True).count()

    @admin.display(description='Постится', boolean=True)
    def will_post(self, obj):
        return TeacherFacultyResult.objects.filter(teacher_id=obj.id).exists()

    class WillPostFiler(BooleanFilterBase):
        title = parameter_name = "Постится"

        def queryset(self, request, queryset):
            q = Q(Exists(TeacherFacultyResult.objects.filter(teacher_id=OuterRef('id'))))
            return queryset.filter(q if self.value() == 'True' else ~q)

    univer_field_path = "univer"
    readonly_fields = ('rozklad_link', 'slug')
    list_display = ('name', 'lessons', 'cathedras', 'faculties', 'photo_img', 'will_post', 'votes_count')
    list_editable = ('lessons',)
    list_filter = (
        ('groups__faculty', RelatedFieldListFilterByUniver),
        ('univer', admin.RelatedOnlyFieldListFilter),
        ("photo", admin.EmptyFieldListFilter),
        WillPostFiler
    )
    search_fields = ('name',)
    inlines = (GroupInline,)
    ordering = ('name',)
    formfield_overrides = {models.TextField: {'widget': Textarea(attrs={'wrap': 'off', 'rows': 4})}}


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Faculty)
class FacultyAdmin(ModelAdminByUniver):
    univer_field_path = "univer"
    search_fields = ('name',)
    list_display = ('name', 'univer', 'poll_result_link')
    list_editable = ('poll_result_link',)
    list_filter = ('univer',)


@admin.register(Question)
class QuestionAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'question_text', 'answer_tip', 'is_for_eng', 'is_for_lec', 'is_for_pra', 'is_two_answers')
    list_editable = ('question_text', 'answer_tip',)
    formfield_overrides = {models.TextField: {'widget': Textarea(attrs={'rows': 2})}}


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

    list_display = ('user_id', 'teacher', 'group', 'teacher_type', 'is_active')
    list_filter = (
        'is_active', 'open_answer_moderate',
        ('teacher_n_group__teacher', admin.RelatedOnlyFieldListFilter),
        ('teacher_n_group__group', admin.RelatedOnlyFieldListFilter),
    )
    readonly_fields = ('teacher_n_group', 'time_start', 'time_finish')
    inlines = (AnswerInline,)


@admin.register(TeacherFacultyResult)
class ResultFacultyAdmin(admin.ModelAdmin):
    @admin.display(description='Позыркать')
    def view(self, obj):
        return mark_safe(f'<a href="/pic/{obj.teacher.id}/{obj.faculty.id}">/pic/{obj.teacher.id}/{obj.faculty.id}</a>')

    list_display = ('teacher', 'faculty', 'teacher_type', 'view')
    list_filter = (
        ('teacher', admin.RelatedOnlyFieldListFilter),
        ('faculty', admin.RelatedOnlyFieldListFilter),
    )
