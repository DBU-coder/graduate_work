# Generated by Django 4.1.4 on 2022-12-18 15:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rims',
            name='description',
            field=models.TextField(blank=True, verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='tires',
            name='description',
            field=models.TextField(blank=True, verbose_name='Описание'),
        ),
    ]
