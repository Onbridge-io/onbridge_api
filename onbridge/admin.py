from django.contrib import admin

from . import models


class IndexerAdmin(admin.ModelAdmin):
    list_display = ('chain_id', 'indexed_block')

    class Meta:
        model = models.Indexer


class TokenAdmin(admin.ModelAdmin):
    list_display = ('token_id', 'owner', 'chain_id', 'block_number', 'skill')
    search_fields = ('owner', )
    list_filter = ('chain_id', )

    class Meta:
        model = models.Token


class ActionBridgeAdmin(admin.ModelAdmin):
    list_display = ('bridge_sender', 'bridge_receiver', 'direction', 'token', 'status')

    class Meta:
        model = models.ActionBridge


admin.site.register(models.Indexer, IndexerAdmin)
admin.site.register(models.Token, TokenAdmin)
admin.site.register(models.ActionBridge, ActionBridgeAdmin)
