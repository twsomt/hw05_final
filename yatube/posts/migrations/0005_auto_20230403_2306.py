# Generated by Django 2.2.19 on 2023-04-03 23:06

from django.db import migrations, models
import posts.models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0004_auto_20230403_1605'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, help_text='Выберите изображение для публикации', upload_to=posts.models.user_directory_path, verbose_name='Изображение'),
        ),
    ]
