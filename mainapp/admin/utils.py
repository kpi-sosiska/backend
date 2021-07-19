from collections import defaultdict

from django.contrib import admin
from django.http import HttpResponse


class ModelAdminByUniver(admin.ModelAdmin):
    univer_field_path = None

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if self.univer_field_path and request.user.univer:
            queryset = queryset.filter(**{self.univer_field_path: request.user.univer})
        return queryset


class RelatedFieldListFilterByUniver(admin.RelatedFieldListFilter):
    def field_choices(self, field, request, model_admin):
        limit = {'univer': request.user.univer} if model_admin.univer_field_path and request.user.univer else {}
        ordering = self.field_admin_ordering(field, request, model_admin)
        return field.get_choices(include_blank=False, ordering=ordering, limit_choices_to=limit)


@admin.action(description='Получить ссылки на прохождение опроса')
def export_groups(model_admin, request, queryset):
    fac2group = defaultdict(list)
    for group in queryset:
        fac2group[group.faculty.name].append(group)

    text = "\n".join([
        f"{fac: ^30}\n" +
        '\n'.join([
            f"{group.name: <20} {group.link()}"
            for group in groups
        ])
        for fac, groups in fac2group.items()
    ])
    return HttpResponse(f"<pre>{text}</pre>")


def short_fio(t):
    if '.' in t:
        return t
    try:
        p = t.split(' ')
        return f"{p[0]} {p[1][0]}. {p[2][0]}"
    except:
        return t