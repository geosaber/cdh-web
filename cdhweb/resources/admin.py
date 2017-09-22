from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from mezzanine.pages.models import Page, RichTextPage
from mezzanine.pages.admin import PageAdmin

from cdhweb.resources.models import ResourceType, Attachment, LandingPage


class ResourceTypeAdmin(admin.ModelAdmin):
    # TODO: drag and drop to set sort order in future
    list_display = ('name', 'sort_order')
    list_editable = ('sort_order', )

# customize default User display
class LocalUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ('is_superuser', 'is_active',
        'last_login')

# NOTE: using inlines for event, project, and profile attachments
# this is clunky, but at least makes the relationships visible
# when looking at the attachment file

class EventAttachmentInline(admin.TabularInline):
    model = Attachment.event_set.through
    extra = 1

class ProfileAttachmentInline(admin.TabularInline):
    model = Attachment.profile_set.through
    extra = 1

class ProjectAttachmentInline(admin.TabularInline):
    model = Attachment.project_set.through
    extra = 1

class BlogpostAttachmentInline(admin.TabularInline):
    model = Attachment.blogpost_set.through
    extra = 1


class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'attachment_type')
    filter_horizontal = ('pages', )
    fields = ('title', 'author', 'file', 'url', 'attachment_type',
        'pages')
    inlines = [EventAttachmentInline, ProfileAttachmentInline,
        ProjectAttachmentInline, BlogpostAttachmentInline]

class PageAttachmentInline(admin.TabularInline):
    model = Page.attachments.through
    extra = 1

class LocalPageAdmin(PageAdmin):
    inlines = [PageAttachmentInline]


admin.site.register(ResourceType, ResourceTypeAdmin)
admin.site.register(Attachment, AttachmentAdmin)
admin.site.register(LandingPage, LocalPageAdmin)
# unregister and re-register mezzzanine page
admin.site.unregister(RichTextPage)
admin.site.register(RichTextPage, LocalPageAdmin)
# unregister and re-register User
admin.site.unregister(User)
admin.site.register(User, LocalUserAdmin)




