# Generated by Django 3.2.19 on 2023-05-19 06:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_rename_tags_recipe_tag'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipe',
            old_name='tag',
            new_name='tags',
        ),
    ]
