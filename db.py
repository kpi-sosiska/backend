from pathlib import Path

from peewee import SqliteDatabase, Model, CharField, ForeignKeyField, fn, IntegerField

PATH_DB = Path(__name__).parent / 'db.sqlite'
DB = SqliteDatabase(PATH_DB)


class BaseModel(Model):
    class Meta:
        database = DB


class Group(BaseModel):
    id = IntegerField(primary_key=True)
    group_name = CharField(max_length=20)
    faculty = CharField(max_length=20, null=True)

    @classmethod
    def add(cls, group_id, group_name, faculty):
        cls.create(
            id=group_id,
            group_name=group_name,
            faculty=faculty
        )

    @classmethod
    def get_groups(cls):
        return [i.id for i in cls.select(cls.id)]


class Teacher(BaseModel):
    teacher_name = CharField(max_length=1000)
    teacher_type = CharField(max_length=10, null=True)
    group = ForeignKeyField(Group)

    @classmethod
    def add(cls, teacher, group_id):
        cls.create(
            teacher_name=teacher[0],
            teacher_type=teacher[1],
            group=group_id
        )

    class Meta:
        indexes = (  # связка уникальных полей
            (('teacher_name', 'group'), True),
        )


DB.create_tables([Group, Teacher])
