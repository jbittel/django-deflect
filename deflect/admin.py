from django.contrib import admin

from .models import RedirectURL


class RedirectURLAdmin(admin.ModelAdmin):
    list_display = ('url', 'short_url', 'hits', 'last_used', 'creator', 'campaign', 'medium',)
    list_filter = ('creator__username', 'campaign', 'medium',)
    ordering = ('-last_used',)
    readonly_fields = ('created', 'short_url', 'qr_code', 'hits', 'last_used',)
    search_fields = ['url', 'campaign']

    fieldsets = ((None, {'fields': ('url', 'short_url',)}),
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
