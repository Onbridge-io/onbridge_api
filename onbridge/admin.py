from django.contrib import admin

from . import models


class StatusAdmin(admin.ModelAdmin):
    class Meta:
        model = models.Status


class TokenAdmin(admin.ModelAdmin):
    class Meta:
        model = models.Token


admin.site.register(models.Status, StatusAdmin)
admin.site.register(models.Token, TokenAdmin)
