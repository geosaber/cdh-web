from django.conf.urls import url

from . import views


urlpatterns = [
    url('^$', views.UpcomingEventsView.as_view(), name='list'),
    url('^(?P<year>\d{4})/$', views.EventYearArchiveView.as_view(),
        name='by-year'),
    url("^(?P<year>\d{4})/(?P<month>\d{2})/(?P<slug>[\w-]+)/$",
        views.EventDetailView.as_view(), name='detail'),
    url("^(?P<year>\d{4})/(?P<month>\d{2})/(?P<slug>[\w-]+).ics$",
        views.EventIcalView.as_view(), name='ical'),
]
