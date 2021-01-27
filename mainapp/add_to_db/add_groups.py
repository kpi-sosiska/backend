from mainapp.add_to_db._base import reader
from mainapp.models import atomic, Group, Faculty

with atomic():
    with reader('groups') as csv_reader:
        for row in csv_reader:
            group, faculty_name, *_ = row
            group_name, group_id = group.split('_')

            faculty, _ = Faculty.objects.get_or_create(name=faculty_name)

            Group(
                id=group_id,
                name=group_name,
                faculty=faculty
            ).save()
