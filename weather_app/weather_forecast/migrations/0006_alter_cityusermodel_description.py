# Generated by Django 4.1.6 on 2023-02-13 19:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('weather_forecast', '0005_cityusermodel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cityusermodel',
            name='description',
            field=models.TextField(blank=True, default='', null=True),
        ),
    ]
