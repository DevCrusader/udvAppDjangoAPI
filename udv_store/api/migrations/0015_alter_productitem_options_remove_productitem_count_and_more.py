# Generated by Django 4.0.3 on 2022-05-13 20:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_remove_cart_product_id_cart_product_item_id'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='productitem',
            options={'verbose_name': 'Категория товара', 'verbose_name_plural': 'Категории товаров'},
        ),
        migrations.RemoveField(
            model_name='productitem',
            name='count',
        ),
        migrations.AddField(
            model_name='productitem',
            name='archived_sizes',
            field=models.CharField(default='', max_length=50),
        ),
    ]
