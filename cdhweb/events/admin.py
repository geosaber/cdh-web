from django.contrib import admin

from .models import EventType, Location, Event

class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_type', 'start_time', 'admin_thumb',
        'tag_list')
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = 'start_time'
    search_fields = ('title', 'content')
    list_filter = ('event_type',)
    filter_horizontal = ('attachments', )

    def tag_list(self, obj):
        return u", ".join(o.name for o in obj.tags.all())
    tag_list.short_description = 'Tags'

    # use inline fields for titles and resources
    # also: suppress management/auth fields like password, username, permissions,
    # last login and date joined

class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name', 'address')


admin.site.register(EventType)
admin.site.register(Location, LocationAdmin)
admin.site.register(Event, EventAdmin)

