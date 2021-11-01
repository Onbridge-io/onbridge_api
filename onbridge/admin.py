from django.contrib import admin

from . import models


class StatusAdmin(admin.ModelAdmin):
    class Meta:
        model = models.Status


class TokenAdmin(admin.ModelAdmin):
    class Meta:
        model = models.Token


class ActionAdmin(admin.ModelAdmin):
    class Meta:
        model = models.Action


admin.site.register(models.Status, StatusAdmin)
admin.site.register(models.Token, TokenAdmin)
admin.site.register(models.Action, ActionAdmin)
