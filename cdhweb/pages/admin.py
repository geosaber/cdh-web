from django.contrib import admin
from wagtail.core.models import Page, Site
from wagtail.documents.models import Document
from wagtail.images.models import Image

# unregister wagtail content from django admin to avoid
# editing something in the wrong place and potentially causing
# problems

admin.site.unregister(Page)
admin.site.unregister(Site)
admin.site.unregister(Image)
admin.site.unregister(Document)