# Generated by Django 2.1.7 on 2019-02-19 15:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qa', '0002_auto_20190219_1439'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answerlike',
            name='is_positive',
            field=models.NullBooleanField(default=None),
        ),
        migrations.AlterField(
            model_name='questionlike',
            name='is_positive',
            field=models.NullBooleanField(default=None),
        ),
    ]