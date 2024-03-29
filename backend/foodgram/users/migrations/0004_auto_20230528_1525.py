# Generated by Django 3.2 on 2023-05-28 15:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.expressions


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20230528_1403'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subscriptions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subscriber', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscriber', to=settings.AUTH_USER_MODEL, verbose_name='Подписчик')),
                ('subscription', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscription', to=settings.AUTH_USER_MODEL, verbose_name='Подписка')),
            ],
        ),
        migrations.AddConstraint(
            model_name='subscriptions',
            constraint=models.UniqueConstraint(fields=('subscriber', 'subscription'), name='uniqie_subscriber_subscription'),
        ),
        migrations.AddConstraint(
            model_name='subscriptions',
            constraint=models.CheckConstraint(check=models.Q(_negated=True, subscriber=django.db.models.expressions.F('subscription')), name='check_self_subscription'),
        ),
    ]
