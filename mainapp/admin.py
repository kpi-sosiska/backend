from collections import defaultdict

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .models import Locale, Question, Teacher, Result, ResultAnswers, Group, TeacherNGroup, Faculty, CustomUser, \
    University


class ModelAdminByUniver(admin.ModelAdmin):
    univer_field_path = None

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if self.univer_field_path and request.user.univer:
            queryset = queryset.filter(**{self.univer_field_path: request.user.univer})
        return queryset


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
    def export(self, request, queryset):
        fac2group = defaultdict(list)
        for group in queryset:
            fac2group[group.faculty.name].append(group)
        text = "\n".join([
            f"{fac: ^30}\n" + '\n'.join([
                f"{group.name: <20} {group.link()}"
                for group in groups
            ])
            for fac, groups in fac2group.items()
        ])
        return HttpResponse(f"<pre>{text}</pre>")

    @admin.display(description='Ссылка на розклад')
    def rozklad_link(self, obj):
        return mark_safe(f'<a href="http://rozklad.kpi.ua/Schedules/ViewSchedule.aspx?g={obj.id}">{obj.id}</a>')

    @admin.display(description='Преподы')
    def teacher_list(self, obj):
        def shortify(t):
            if '.' in t:
                return t
            try:
                p = t.split(' ')
                return f"{p[0]} {p[1][0]}. {p[2][0]}"
            except:
                return t
        teachers = obj.teachers.all().values_list('name', flat=True).order_by('name').distinct()
        teachers = [shortify(t) for t in teachers]
        return '; '.join(teachers)

    class TeacherInline(admin.TabularInline):
        autocomplete_fields = ('teacher',)
        model = TeacherNGroup
        extra = 1

    univer_field_path = "faculty__univer"
    readonly_fields = ('rozklad_link', 'link')
    autocomplete_fields = ('faculty',)
    list_display = ('name', 'faculty', 'teacher_list')
    list_filter = ('faculty', 'faculty__univer')
    search_fields = ('name',)
    actions = ('export',)
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
        if not obj.photo:
            return None
        return mark_safe(f'<img src="{obj.photo}" width="50px">')

    univer_field_path = "univer"
    readonly_fields = ('rozklad_link',)
    list_display = ('name', 'lessons', 'cathedras', 'faculties', 'photo_img')
    list_editable = ('lessons',)
    list_filter = ('groups__faculty', 'univer', ("photo", admin.EmptyFieldListFilter))
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

    class IsFinishedListFilter(admin.SimpleListFilter):
        title = 'Закончил опрос'
        parameter_name = 'is_finished'

        def lookups(self, request, model_admin):
            return (('1', 'Закончил опрос'),
                    ('0', 'Не закончил опрос'))

        def queryset(self, request, queryset):
            if self.value() is None:
                return queryset
            is_finished = int(self.value() or 0)
            return queryset.filter(time_finish__isnull=not is_finished)

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
