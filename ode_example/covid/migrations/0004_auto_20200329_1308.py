# Generated by Django 3.0.4 on 2020-03-29 13:08

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('covid', '0003_auto_20200328_1839'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ode',
            name='max_t',
            field=models.IntegerField(default=10, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='ode',
            name='recovery_rate',
            field=models.FloatField(default=1, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
        migrations.AlterField(
            model_name='ode',
            name='transmission_rate',
            field=models.FloatField(default=10, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
    ]