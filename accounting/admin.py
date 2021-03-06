from django.contrib import admin

from tokenManager.models import TokenManager
from accounting.models import Account


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    pass


@admin.register(TokenManager)
class TokenAdmin(admin.ModelAdmin):
    pass

