import re

from django import forms
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
            r = requests.head(url, allow_redirects=True)
        except requests.exceptions.ConnectionError:
            raise forms.ValidationError("Error connecting to URL")
        except requests.exceptions.SSLError:
            raise forms.ValidationError("Invalid SSL certificate")

        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            raise forms.ValidationError("Invalid status returned (%d)" % r.status_code)

        return r.url


class ShortURLAdmin(admin.ModelAdmin):
    form = ShortURLAdminForm
    inlines = [ShortURLAliasInline]
    list_display = ('long_url', 'short_url', 'hits', 'last_used', 'creator', 'campaign', 'medium')
    list_filter = ('creator__username', 'campaign', 'medium')
    ordering = ['-last_used']
    readonly_fields = ('created', 'short_url', 'qr_code', 'hits', 'last_used')
    search_fields = ['long_url', 'campaign', 'shorturlalias__alias']

    fieldsets = ((None, {'fields': ('long_url', 'short_url')}),
                 ('Google', {'fields': ('campaign', 'medium', 'content')}),
                 ('Additional Info', {'fields': ('description', 'qr_code')}),
                 ('Short URL Usage', {'classes': ('collapse grp-collapse grp-closed'),
                                      'fields': ('hits', 'created', 'last_used')}))

    def has_change_permission(self, request, obj=None):
        """
        Users should only be able to modify ``ShortURL``s they own,
        except for superusers.
        """
        has_class_permission = super(ShortURLAdmin, self).has_change_permission(request, obj)
        if not has_class_permission:
            return False
        if obj is not None and not request.user.is_superuser and request.user.id != obj.creator.id:
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        """
        Users should only be able to delete ``ShortURL``s they own,
        except for superusers.
        """
        has_class_permission = super(ShortURLAdmin, self).has_delete_permission(request, obj)
        if not has_class_permission:
            return False
        if obj is not None and not request.user.is_superuser and request.user.id != obj.creator.id:
            return False
        return True

    def queryset(self, request):
        """
        Superusers can view all ``ShortURL``s. Non-superusers should
        only be able to view their own.
        """
        qs = super(ShortURLAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(creator=request.user)

    def save_model(self, request, obj, form, change):
        """
        On first save, set the ``ShortURL`` creator to the current
        user. On subsequent saves, skip this step.
        """
        if not change:
            obj.creator = request.user
        obj.save()


admin.site.register(ShortURL, ShortURLAdmin)
