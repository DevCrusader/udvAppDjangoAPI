# Generated by Django 4.0.3 on 2022-06-13 13:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0023_userinfo_ava_back_color_userinfo_ava_main_color_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='category_id',
        ),
        migrations.DeleteModel(
            name='Category',
        ),
    ]
