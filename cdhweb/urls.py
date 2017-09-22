from __future__ import unicode_literals

from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
# from django.conf.urls.static import static
from django.contrib import admin
from django.views.i18n import set_language
from django.views.generic.base import RedirectView

from mezzanine.conf import settings

from cdhweb.resources import views as resource_views

admin.autodiscover()

# Add the urlpatterns for any custom Django applications here.
# You can also change the ``home`` view to add your own functionality
# to the project's homepage.

urlpatterns = i18n_patterns(
    # Change the admin prefix here to use an alternate URL for the
    # admin interface, which would be marginally more secure.
    url("^admin/", include(admin.site.urls)),
)

if settings.USE_MODELTRANSLATION:
    urlpatterns += [
        url('^i18n/$', set_language, name='set_language'),
    ]

urlpatterns += [
    url("^people/", include("cdhweb.people.urls", namespace='people')),
    # actual blog url still TBD
    url("^updates/", include("cdhweb.blog.urls", namespace='blog')),
    url("^events/", include("cdhweb.events.urls", namespace='event')),
    url("^projects/", include("cdhweb.projects.urls", namespace='project')),

    url("^$", resource_views.Homepage.as_view(), name="home"),

    # CAS login urls
    url(r'^accounts/', include('pucas.cas_urls')),

    # programmatic redirects from v1 site
    # - old staff page is now under /people/
    url(r'^about/staff/(?P<slug>[\w-]+)/$',
        RedirectView.as_view(pattern_name='people:profile', permanent=True),
        name='old-profile'),
    # - all blog urls are now under updates/
    url(r'^blog(?P<blog_url>.*)$',
        RedirectView.as_view(url='/updates%(blog_url)s', permanent=True)),

    # let mezzanine handle everything else
    url("^", include("mezzanine.urls")),
]

# Adds ``STATIC_URL`` to the context of error pages, so that error
# pages can use JS, CSS and images.
handler404 = "mezzanine.core.views.page_not_found"
handler500 = "mezzanine.core.views.server_error"
