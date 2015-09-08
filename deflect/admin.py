import re

from django import forms
from django.conf import settings
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
        headers = getattr(settings, 'DEFLECT_REQUESTS_HEADERS', None)
        timeout = getattr(settings, 'DEFLECT_REQUESTS_TIMEOUT', 3.0)
        try:
            r = requests.get(url, headers=headers, timeout=timeout,
                             allow_redirects=True)
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
    list_display = ('long_url', 'short_url', 'created', 'hits', 'last_used', 'campaign', 'medium')
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
        """
        If a ``ShortURL`` has already been created, then display the
        configured readonly fields. Otherwise, hide them as they
        will not contain data in that context.
        """
        if obj:
            return self.readonly_fields
        return ()

    def get_fieldsets(self, request, obj=None):
        """
        Display the appropriate fieldsets depending on whether a
        ``ShortURL`` is being added or changed.
        """
        if obj:
            return self._change_fieldsets
        return self._add_fieldsets

    def changelist_view(self, request, extra_context=None):
        """
        Inject additional filtering options for users with
        appropriate permissions.
        """
        if request.user.has_perm('deflect.list_all'):
            self.list_filter = self._list_filter + ('creator__username',)
            self.list_display = self._list_display + ('creator',)
        else:
            self.list_filter = self._list_filter
            self.list_display = self._list_display
        return super(ShortURLAdmin, self).changelist_view(request, extra_context=extra_context)

    def has_change_permission(self, request, obj=None):
        """
        Users should only be able to modify ``ShortURL``s they own,
        except for privileged users.
        """
        has_perm = super(ShortURLAdmin, self).has_change_permission(request, obj)
        if not has_perm:
            return False
        if obj is not None and not request.user.has_perm('deflect.list_all') and request.user.id != obj.creator.id:
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        """
        Users should only be able to delete ``ShortURL``s they own,
        except for privileged users.
        """
        has_perm = super(ShortURLAdmin, self).has_delete_permission(request, obj)
        if not has_perm:
            return False
        if obj is not None and not request.user.has_perm('deflect.list_all') and request.user.id != obj.creator.id:
            return False
        return True

    def queryset(self, request):
        """
        Users should only be able to view their own ``ShortURL``s,
        except for privileged users.
        """
        qs = super(ShortURLAdmin, self).queryset(request)
        if request.user.has_perm('deflect.list_all'):
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
