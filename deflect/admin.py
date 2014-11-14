import re

from django import forms
from django.contrib import admin

import requests

from .models import ShortURL
from .models import ShortURLAlias
from .widgets import DatalistTextInput


class ShortURLAliasAdminForm(forms.ModelForm):
    def clean_alias(self):
        """
        Validate characters for the provided alias.
        """
        alias = self.cleaned_data.get('alias')
        if not bool(re.compile(r'^[a-zA-Z0-9-]+$').match(alias)):
            raise forms.ValidationError("Alias contains invalid characters")
        return alias


class ShortURLAliasInline(admin.StackedInline):
    model = ShortURLAlias
    form = ShortURLAliasAdminForm


class ShortURLAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ShortURLAdminForm, self).__init__(*args, **kwargs)
        self.fields['campaign'].widget = DatalistTextInput(choices=ShortURL.objects.get_unique_list('campaign'))
        self.fields['medium'].widget = DatalistTextInput(choices=ShortURL.objects.get_unique_list('medium'))

    def clean_long_url(self):
        """
        Validate connectivity to the provided target URL.
        """
        url = self.cleaned_data.get('long_url')
        try:
            r = requests.head(url, allow_redirects=True, timeout=3.0)
        except requests.exceptions.ConnectionError:
            raise forms.ValidationError("Error connecting to URL")
        except requests.exceptions.SSLError:
            raise forms.ValidationError("Invalid SSL certificate")
        except requests.exceptions.Timeout:
            raise forms.ValidationError("Timeout connecting to URL")

        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            raise forms.ValidationError("Invalid status returned (%d)" % r.status_code)

        return r.url


class ShortURLAdmin(admin.ModelAdmin):
    form = ShortURLAdminForm
    inlines = [ShortURLAliasInline]
    list_display = ('long_url', 'short_url', 'created', 'last_used', 'campaign', 'medium')
    _list_display = list_display
    list_filter = ('campaign', 'medium')
    _list_filter = list_filter
    ordering = ['-created']
    readonly_fields = ('created', 'short_url', 'target_url', 'qr_code', 'hits', 'last_used')
    search_fields = ['long_url', 'campaign', 'shorturlalias__alias']

    _change_fieldsets = ((None, {'fields': ('long_url', 'short_url', 'target_url')}),
                 ('Tracking', {'fields': ('is_tracking', 'campaign', 'medium', 'content')}),
                 ('Additional Info', {'fields': ('description', 'qr_code')}),
                 ('Short URL Usage', {'classes': ('collapse', 'grp-collapse', 'grp-closed'),
                                      'fields': ('hits', 'created', 'last_used')}))

    _add_fieldsets = ((None, {'fields': ('long_url',)}),
                 ('Tracking', {'fields': ('is_tracking', 'campaign', 'medium', 'content')}),
                 ('Additional Info', {'fields': ('description',)}))

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields
        return ()

    def get_fieldsets(self, request, obj=None):
        if obj:
            return self._change_fieldsets
        return self._add_fieldsets

    def changelist_view(self, request, extra_context=None):
        """
        Inject additional filtering options for superusers.
        """
        if request.user.is_superuser:
            self.list_filter = self._list_filter + ('creator__username',)
            self.list_display = self._list_display + ('creator',)
        else:
            self.list_filter = self._list_filter
            self.list_display = self._list_display
        return super(ShortURLAdmin, self).changelist_view(request, extra_context=extra_context)

    def has_change_permission(self, request, obj=None):
        """
        Users should only be able to modify ``ShortURL``s they own,
        except for superusers.
        """
        has_perm = super(ShortURLAdmin, self).has_change_permission(request, obj)
        if not has_perm:
            return False
        if obj is not None and not request.user.is_superuser and request.user.id != obj.creator.id:
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        """
        Users should only be able to delete ``ShortURL``s they own,
        except for superusers.
        """
        has_perm = super(ShortURLAdmin, self).has_delete_permission(request, obj)
        if not has_perm:
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
