# Generated by Django 4.1.1 on 2022-10-15 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('statuses', '0003_alter_statusmodel_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='statusmodel',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания'),
        ),
    ]