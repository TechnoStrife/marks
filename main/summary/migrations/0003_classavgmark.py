# Generated by Django 2.2.1 on 2019-07-23 13:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0012_auto_20190710_1214'),
        ('summary', '0002_auto_20190710_1601'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClassAvgMark',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mark', models.FloatField(null=True)),
                ('terminal_mark', models.SmallIntegerField(null=True)),
                ('diff', models.FloatField(null=True)),
                ('klass', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Class')),
            ],
        ),
    ]
