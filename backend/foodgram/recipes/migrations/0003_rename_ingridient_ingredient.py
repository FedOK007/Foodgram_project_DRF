# Generated by Django 3.2 on 2023-05-30 20:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_ingridient'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Ingridient',
            new_name='Ingredient',
        ),
    ]