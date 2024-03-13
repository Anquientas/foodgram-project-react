# Generated by Django 3.2.16 on 2024-03-13 17:42

from django.db import migrations, models
import tags.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Введите название тега', max_length=200, verbose_name='Название')),
                ('color', models.CharField(help_text='Введите цвет в HEX-формате', max_length=7, validators=[tags.validators.validate_color], verbose_name='Цвет в HEX')),
                ('slug', models.CharField(help_text='Введите уникальный слаг', max_length=200, unique=True, validators=[tags.validators.validate_slug], verbose_name='Уникальный слаг')),
            ],
            options={
                'verbose_name': 'Тег',
                'verbose_name_plural': 'Теги',
                'ordering': ('name',),
            },
        ),
    ]
