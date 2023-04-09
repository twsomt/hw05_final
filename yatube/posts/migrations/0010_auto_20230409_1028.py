# Generated by Django 2.2.19 on 2023-04-09 10:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0009_auto_20230408_0856'),
    ]

    operations = [
        migrations.AlterField(
            model_name='follow',
            name='user',
            field=models.ForeignKey(blank=True, help_text='Пользователь, подписавшийся на автора', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='follower', to=settings.AUTH_USER_MODEL, verbose_name='Подписчик'),
        ),
    ]