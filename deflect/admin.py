from django import forms
from django.conf import settings
from django.contrib import admin

import requests

from .models import CustomURL
from .models import RedirectURL


class RedirectURLAdminForm(forms.ModelForm):
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


class CustomURLInline(admin.StackedInline):
    model = CustomURL


class RedirectURLAdmin(admin.ModelAdmin):
    form = RedirectURLAdminForm
    list_display = ('long_url', 'short_url', 'hits', 'last_used', 'creator', 'campaign', 'medium',)
    list_filter = ('creator__username', 'campaign', 'medium',)
    ordering = ('-last_used',)
    readonly_fields = ('created', 'short_url', 'qr_code', 'hits', 'last_used',)
    search_fields = ['long_url', 'campaign',]

    # Only display the custom alias field if a prefix has been configured
    alias_prefix = getattr(settings, 'DEFLECT_ALIAS_PREFIX', '')
    if alias_prefix:
        inlines = [CustomURLInline,]

    fieldsets = ((None, {'fields': ('long_url', 'short_url',)}),
                 ('Google', {'fields': ('campaign', 'medium', 'content',)}),
                 ('Additional Info', {'fields': ('description', 'qr_code',)}),
                 ('Short URL Usage', {'classes': ('collapse grp-collapse grp-closed',),
                                      'fields': ('hits', 'created', 'last_used',)}),)

    def save_model(self, request, obj, form, change):
        """
        On first save, set the ``RedirectURL`` creator to the current
        user. On subsequent saves, skip this step.
        """
        if not change:
            obj.creator = request.user
        obj.save()


admin.site.register(RedirectURL, RedirectURLAdmin)
