# Generated by Django 3.1.5 on 2021-01-27 02:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0007_remove_result_continue_teach_answer'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='result',
            unique_together={('user_id', 'teacher_n_group')},
        ),
    ]