from mainapp.add_to_db._base import reader
from mainapp.models import atomic, Group, Faculty, Teacher, TeacherNGroup



def add_teacher(teachers, group_id):
    with atomic():
        teachers_models = []
        for t in teachers:
            if not t:
                continue
            try:
                teacher, _ = Teacher.objects.get_or_create(name=t.replace(' ENG', ''),
                                                        defaults=dict(is_eng='ENG' in t))
                teachers_models.append(teacher)
            except (Teacher.DoesNotExist, Teacher.MultipleObjectsReturned) as ex:
                print(ex, group_id, t, '-')
                return

        for t in teachers_models:
            try:
                TeacherNGroup(group_id=group_id, teacher_id=t.id).save()
            except Exception as ex:
                print(ex, group_id, t.id, t.name)
                return



with reader('groups') as csv_reader:
    for row in csv_reader:
        group, faculty_name, *teachers = row
        group_name, group_id = group.split('_')

        add_teacher(teachers, group_id)



            # faculty, _ = Faculty.objects.get_or_create(name=faculty_name)

            # Group(
            #     id=group_id,
            #     name=group_name,
            #     faculty=faculty
            # ).save()
