from django.conf.urls import url

from . import views


urlpatterns = [
    url('^$', views.UpcomingEventsView.as_view(), name='upcoming'),
    url('^(?P<pk>\d{1,2})/$', views.EventRedirectView.as_view(),
        name='by-id'),
    url('^(?P<semester>(fall|spring|summer))-(?P<year>\d{4})/$',
        views.EventSemesterArchiveView.as_view(), name='by-semester'),
    url("^(?P<year>\d{4})/(?P<month>\d{2})/(?P<slug>[\w-]+)/$",
        views.EventDetailView.as_view(), name='detail'),
    url("^(?P<year>\d{4})/(?P<month>\d{2})/(?P<slug>[\w-]+).ics$",
        views.EventIcalView.as_view(), name='ical'),
]
