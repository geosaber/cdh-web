from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin
from mezzanine.core.admin import DisplayableAdmin

from .models import Project, GrantType, Grant, Membership, Role, \
    ProjectResource

class MemberInline(admin.TabularInline):
    model = Membership

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        field = super(MemberInline, self).formfield_for_foreignkey(db_field, request, **kwargs)
        # restrict only to grants associated with the current project
        if db_field.name == 'grant':
            if request.object is not None:
                field.queryset = field.queryset.filter(project=request.object)
        return field


class ResourceInline(admin.TabularInline):
    model = ProjectResource

class GrantInline(admin.TabularInline):
    model = Grant


class ProjectAdmin(DisplayableAdmin):
    # extend displayable list to add highlight and make it editable
    list_display = ("title", "status", "highlight", "admin_link", "admin_thumb",
        "tag_list")
    list_editable = ("status", "highlight")

    list_filter = ("status", "grant", "keywords__keyword")
    # displayable date hierarchy is publish date, does that make sense here?
    date_hierarchy = "publish_date"
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ('attachments', )

    # fieldset based on displayaable admin with project fields added
    fieldsets = (
        (None, {
            "fields": ["title", "status", ("publish_date", "expiry_date"),
                       "short_description", "long_description", "highlight",
                       "image", "thumb", 'attachments'],  # tags todo
        }),
        ("Meta data", {
            "fields": ["_meta_title", "slug",
                       ("description", "gen_description"),
                        "keywords", "in_sitemap"],
            "classes": ("collapse-closed",)
        }),
    )

    def tag_list(self, obj):
        return u", ".join(o.name for o in obj.tags.all())
    tag_list.short_description = 'Tags'

    inlines = [GrantInline, MemberInline, ResourceInline]

    def get_form(self, request, obj=None, **kwargs):
        # save object reference for filtering grants in membership Inline
        request.object = obj
        return super(ProjectAdmin, self).get_form(request, obj, **kwargs)

class GrantAdmin(admin.ModelAdmin):
    list_display = ('project', 'grant_type', 'start_date', 'end_date')
    date_hierarchy = 'start_date'


class MembershipAdmin(admin.ModelAdmin):
    list_display = ('project', 'user', 'grant', 'role')
    list_filter = ('project', 'role')
    search_fields = ('user__first_name', 'user__last_name', 'project__title')


class RoleAdmin(admin.ModelAdmin):
    # TODO: drag and drop to set sort order in future
# class RoleAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'sort_order')
    list_editable = ('sort_order', )


admin.site.register(Project, ProjectAdmin)
admin.site.register(GrantType)
admin.site.register(Grant, GrantAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(Membership, MembershipAdmin)