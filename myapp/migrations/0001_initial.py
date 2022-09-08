# Generated by Django 4.0.6 on 2022-08-08 16:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import djongo.models.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('_id', djongo.models.fields.ObjectIdField(auto_created=True, primary_key=True, serialize=False)),
                ('BTC_amount', models.FloatField()),
                ('USD_amount', models.FloatField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('price', models.FloatField()),
                ('quantity', models.FloatField()),
                ('status', models.CharField(default='PENDING', max_length=12)),
                ('buy_sell', models.CharField(choices=[('BUY', 'buy'), ('SELL', 'sell')], default='BUY', max_length=12)),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.profile')),
            ],
        ),
    ]