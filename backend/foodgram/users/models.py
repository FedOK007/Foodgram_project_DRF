from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(
        'e-mail',
        blank=False,
        null=False,
        unique=True,
        max_length=254
    )
    first_name = models.CharField(
        'first name',
        max_length=150,
        blank=False,
        null=False
    )
    last_name = models.CharField(
        'last name',
        max_length=150,
        blank=False,
        null=False
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('-username',)

    @property
    def is_admin(self):
        return (
            self.is_superuser or self.is_staff
        )

    def __str__(self):
        return self.username[:settings.CROP_LEN_TEXT]


class Subscriptions(models.Model):
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик'
    )
    subscription = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscription',
        verbose_name='Подписка'
    )

    class Meta:
        verbose_name = 'Подписки'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['subscriber', 'subscription'],
                name='unique_subscriber_subscription'
            ),
            models.CheckConstraint(
                check=~models.Q(subscriber=models.F('subscription')),
                name='check_self_subscription'
            )
        ]
