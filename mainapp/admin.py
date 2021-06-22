from collections import defaultdict

from django.contrib import admin
from django.http import HttpResponse, JsonResponse
from django.utils.safestring import mark_safe

from .models import Locale, Question, Teacher, Result, ResultAnswers, Group, TeacherNGroup, Faculty, Cathedra


@admin.register(Locale)
class LocaleAdmin(admin.ModelAdmin):
    empty_value_display = 'Не заполнено'
    list_display = ('key', 'value')
    list_editable = ('value',)


#

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
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
        return '; '.join(obj.teachers.all().values_list('name', flat=True).distinct())

    class TeacherInline(admin.TabularInline):
        model = TeacherNGroup
        extra = 1

    readonly_fields = ('rozklad_link', 'link')
    list_display = ('name', 'faculty', 'teacher_list')
    list_filter = ('faculty', )
    list_editable = ('faculty', )
    search_fields = ('name',)
    actions = ('export',)
    inlines = [
        TeacherInline,
    ]


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    class GroupInline(admin.TabularInline):
        model = TeacherNGroup
        extra = 0

    @admin.display(description='Факультеты')
    def faculties(self, obj):
        return list(Faculty.objects.filter(group__teachers__id=obj.id).distinct())

    @admin.display(description='Кафедры')
    def _cathedras(self, obj: Teacher):
        return list(obj.cathedras.all().distinct())

    @admin.display(description='Ссылка на розклад')
    def rozklad_link(self, obj):
        return mark_safe(f'<a href="http://rozklad.kpi.ua/Schedules/ViewSchedule.aspx?v={obj.id}">{obj.id}</a>')

    readonly_fields = ('rozklad_link',)
    list_display = ('name', 'faculties', 'lessons', '_cathedras')
    list_editable = ('lessons',)
    list_filter = ('groups__faculty', 'cathedras')
    search_fields = ('name',)
    inlines = (GroupInline, )


# @admin.register(TeacherNGroup)
# class TeacherNGroupAdmin(admin.ModelAdmin):
#     @admin.display(description='Факультет')
#     def faculty(self, obj):
#         return obj.group.faculty
#
#     list_display = ('teacher', 'group', 'faculty', 'link')
#     list_filter = ('group__faculty',)


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    list_display = ('name', 'poll_result_link')
    list_editable = ('poll_result_link',)


@admin.register(Cathedra)
class CathedraAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    list_display = ('name', 'faculty')
    list_filter = ('faculty', )


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

    def export(self, request, queryset):
        data = [
            dict(
                teacher_name=(res.teacher_n_group.teacher.name_position or res.teacher_n_group.teacher.name) +
                             (' ENG' if res.teacher_n_group.teacher.is_eng else ''),
                teacher_type=res.teacher_type,
                group_name=res.teacher_n_group.group.name,
                open_question_answer=res.open_question_answer,
                answers=list(res.resultanswers_set.values('question__question_text', 'answer_1', 'answer_2'))
            )
            for res in queryset
        ]
        return JsonResponse(data, safe=False)

    @admin.display(description='Закончил опрос', boolean=True)
    def is_finished(self, obj):
        return obj.time_finish is not None

    list_display = ('user_id', 'teacher', 'group', 'teacher_type', 'is_finished')
    list_filter = (
        ('teacher_n_group__teacher', admin.RelatedOnlyFieldListFilter),
        ('teacher_n_group__group', admin.RelatedOnlyFieldListFilter),
        IsFinishedListFilter
    )
    readonly_fields = ('time_start', 'time_finish')
    raw_id_fields = ('teacher_n_group',)
    actions = ('export',)
    inlines = (AnswerInline, )
