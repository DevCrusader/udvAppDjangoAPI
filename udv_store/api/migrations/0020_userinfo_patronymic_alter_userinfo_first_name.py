# Generated by Django 4.0.3 on 2022-05-23 14:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0019_balancehistory_ucoin_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinfo',
            name='patronymic',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='userinfo',
            name='first_name',
            field=models.CharField(max_length=50),
        ),
    ]
