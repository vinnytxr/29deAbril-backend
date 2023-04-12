# Generated by Django 4.0.10 on 2023-04-12 00:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0003_alter_course_banner'),
    ]

    operations = [
        migrations.CreateModel(
            name='Learning',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=128)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='learnings', to='courses.course')),
            ],
        ),
    ]