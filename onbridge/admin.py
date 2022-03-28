from django.contrib import admin

from . import models


class StatusAdmin(admin.ModelAdmin):
    list_display = ('chain_id', 'indexed_block')

    class Meta:
        model = models.Status


class TokenAdmin(admin.ModelAdmin):
    list_display = ('token_id', 'owner', 'chain_id', 'block_number', 'skill')

    class Meta:
        model = models.Token


class ActionAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'direction', 'token_id', 'status')

    class Meta:
        model = models.Action


admin.site.register(models.Status, StatusAdmin)
admin.site.register(models.Token, TokenAdmin)
admin.site.register(models.Action, ActionAdmin)
