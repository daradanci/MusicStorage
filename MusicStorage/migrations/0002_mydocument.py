# Generated by Django 4.1.3 on 2022-11-23 17:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MusicStorage', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MyDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('doc', models.FileField(upload_to='')),
            ],
        ),
    ]
