# Generated by Django 3.2.13 on 2023-12-04 20:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('station_tracker', '0002_gas_station_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='gas_station',
            name='GasUpdateId',
            field=models.DecimalField(decimal_places=2, max_digits=5, null=True),
        ),
    ]
