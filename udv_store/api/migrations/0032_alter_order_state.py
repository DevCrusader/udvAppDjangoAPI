# Generated by Django 4.0.3 on 2022-07-31 19:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0031_alter_cart_size_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='state',
            field=models.CharField(choices=[('Completed', 'Completed'), ('In progress', 'In Progress'), ('Accepted', 'Accepted')], db_index=True, default='Accepted', max_length=12),
        ),
    ]
