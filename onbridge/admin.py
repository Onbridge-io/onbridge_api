from django.contrib import admin

from . import models


class TokenAdmin(admin.ModelAdmin):
    class Meta:
        model = models.Token


admin.site.register(models.Token, TokenAdmin)
