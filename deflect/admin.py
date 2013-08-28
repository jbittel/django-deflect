import re

from django import forms
from django.conf import settings
from django.contrib import admin

import requests

from .models import ShortURL
from .models import ShortURLAlias


class ShortURLAliasAdminForm(forms.ModelForm):
    def clean_alias(self):
        """
        Validate characters for the provided alias.
        """
        alias = self.cleaned_data.get('alias')
        if bool(re.compile(r'[^a-zA-Z0-9-]').search(alias)):
            raise forms.ValidationError("Alias contains invalid characters")
        return alias


class ShortURLAliasInline(admin.StackedInline):
    model = ShortURLAlias
    form = ShortURLAliasAdminForm


class ShortURLAdminForm(forms.ModelForm):
    def clean_long_url(self):
        """
        Validate connectivity to the provided target URL.
        """
        url = self.cleaned_data.get('long_url')
        try:
            r = requests.head(url)
        except requests.exceptions.ConnectionError:
            raise forms.ValidationError("Error connecting to URL")
        except requests.exceptions.SSLError:
            raise forms.ValidationError("Invalid SSL certificate")

        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            raise forms.ValidationError("Invalid status returned (%d)" % r.status_code)

        return url


class ShortURLAdmin(admin.ModelAdmin):
    form = ShortURLAdminForm
    list_display = ('long_url', 'short_url', 'shorturlalias', 'hits', 'last_used', 'creator', 'campaign', 'medium',)
    list_filter = ('creator__username', 'campaign', 'medium',)
    ordering = ('-last_used',)
    readonly_fields = ('created', 'short_url', 'qr_code', 'hits', 'last_used',)
    search_fields = ['long_url', 'campaign', 'shorturlalias__alias',]
    inlines = [ShortURLAliasInline,]

    fieldsets = ((None, {'fields': ('long_url', 'short_url',)}),
                 ('Google', {'fields': ('campaign', 'medium', 'content',)}),
                 ('Additional Info', {'fields': ('description', 'qr_code',)}),
                 ('Short URL Usage', {'classes': ('collapse grp-collapse grp-closed',),
                                      'fields': ('hits', 'created', 'last_used',)}),)

    def save_model(self, request, obj, form, change):
        """
        On first save, set the ``ShortURL`` creator to the current
        user. On subsequent saves, skip this step.
        """
        if not change:
            obj.creator = request.user
        obj.save()


admin.site.register(ShortURL, ShortURLAdmin)
