# Generated by Django 2.2.1 on 2019-07-23 16:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('summary', '0004_subjectavgmark_teacheravgmark'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subjectavgmark',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Subject'),
        ),
        migrations.AlterField(
            model_name='teacheravgmark',
            name='teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Teacher'),
        ),
    ]
