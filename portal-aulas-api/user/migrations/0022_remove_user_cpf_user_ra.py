# Generated by Django 4.0.10 on 2024-03-10 00:02

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0021_remove_anotation_link'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='cpf',
        ),
        migrations.AddField(
            model_name='user',
            name='ra',
            field=models.CharField(max_length=8, null=True, unique=True, validators=[django.core.validators.MinLengthValidator(4)], verbose_name='ra'),
        ),
    ]
