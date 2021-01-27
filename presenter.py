import csv
from pathlib import Path

import db
import utils


class _BasePresenter:
    SAVE_PATH = Path(__file__).parent / 'results'

    @classmethod
    def present(cls):
        raise NotImplementedError


class FilePresenter(_BasePresenter):
    SAVE_PATH = _BasePresenter.SAVE_PATH / 'file_present'

    @classmethod
    def present(cls):
        res = db.Teacher.select(
            db.Teacher.group,
            db.fn.GROUP_CONCAT(db.Teacher.teacher_name).alias('teachers')
        ).group_by(db.Teacher.group)

        for i in res:
            cls.save_group(i.group.group_name, i.teachers.split(','))

    @classmethod
    def save_group(cls, group, teachers):
        gc = utils.GroupCode(group)
        path = cls.SAVE_PATH / (gc.faculty or '_хз') / gc.metapotoki / gc.potok / gc.group

        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('w') as f:
            f.write('\n'.join(teachers))


class CSVPresenter(_BasePresenter):
    SAVE_PATH = _BasePresenter.SAVE_PATH / 'csv_present.csv'

    @classmethod
    def present(cls):
        table = db.Teacher.select()
        cls.save([
            (i.teacher_name, i.teacher_type, i.group.group_name, i.group.id, i.group.faculty)
            for i in table
        ])

    @classmethod
    def save(cls, rows):
        with cls.SAVE_PATH.open('w') as f:
            writer = csv.writer(f)
            writer.writerows(rows)


if __name__ == '__main__':
    CSVPresenter.present()
