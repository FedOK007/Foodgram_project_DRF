from django.contrib import admin
from django.contrib.auth import get_user_model

from users.models import Subscriptions

User = get_user_model()


class UserAdmin(admin.ModelAdmin):
    list_display = ('username',
                    'email',
                    )
    # list_editable = ('email',)
    search_fields = ('username', 'email',)
    # list_filter = ('username',)
    empty_value_display = '-пусто-'


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('subscriber', 'subscription')
    search_fields = ('subscriber', 'subscription',)
    empty_value_display = '-пусто-'


# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Subscriptions, SubscriptionAdmin)
