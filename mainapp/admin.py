from collections import defaultdict

from django.contrib import admin
from django.http import HttpResponse, JsonResponse

from .models import Locale, Question, Teacher, Result, ResultAnswers, Group, TeacherNGroup, Faculty, Cathedra


@admin.register(Locale)
class LocaleAdmin(admin.ModelAdmin):
    empty_value_display = 'Не заполнено'
    list_display = ('key', 'value')
    list_editable = ('value', )


#

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    def export(self, request, queryset):
        cath2group = defaultdict(list)
        for group in queryset:
            cath2group[group.cathedra.name].append(group)
        text = "\n".join([
            f"{fac: ^30}\n" + '\n'.join([
                f"{group.name: <20} {group.link()}"
                for group in groups
            ])
            for fac, groups in cath2group.items()
        ])
        return HttpResponse(f"<pre>{text}</pre>")

    class TeacherInline(admin.TabularInline):
        model = TeacherNGroup
        extra = 1

    list_display = ('name', 'cathedra', 'link')
    list_filter = ('cathedra', )
    search_fields = ('name', )
    actions = ('export', )
    inlines = [
        TeacherInline,
    ]


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    def faculties(self, obj):
        return list(Faculty.objects.filter(group__teachers__id=obj.id).distinct())

    list_display = ('name', 'faculties')


@admin.register(TeacherNGroup)
class TeacherNGroupAdmin(admin.ModelAdmin):
    def faculty(self, obj):
        return obj.group.faculty

    list_display = ('teacher', 'group', 'faculty', 'link')


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('name', 'poll_result_link')
    list_editable = ('poll_result_link', )


@admin.register(Cathedra)
class CathedraAdmin(admin.ModelAdmin):
    list_display = ('name', 'faculty')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'answer_tip', 'is_for_eng', 'is_for_lec', 'is_for_pra', 'is_two_answers')
    list_editable = ('answer_tip', )


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    class AnswerInline(admin.TabularInline):
        model = ResultAnswers
        extra = 0

    def teacher(self, obj):
        return obj.teacher_n_group.teacher

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

    list_display = ('user_id', 'teacher', 'group', 'teacher_type')
    list_filter = (
        ('teacher_n_group__teacher', admin.RelatedOnlyFieldListFilter),
        ('teacher_n_group__group', admin.RelatedOnlyFieldListFilter)
    )
    readonly_fields = ('date',)
    raw_id_fields = ('teacher_n_group', )
    actions = ('export', )
    inlines = [
        AnswerInline,
    ]

