# Generated by Django 2.1.7 on 2019-02-19 14:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qa', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answerlike',
            name='is_positive',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='questionlike',
            name='is_positive',
            field=models.BooleanField(default=True),
        ),
    ]
