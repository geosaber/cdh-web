from django.conf.urls import url

from . import views


urlpatterns = [
    url('^$', views.BlogIndexView.as_view(), name='list'),
    url('^(?P<year>\d{4})/$', views.BlogYearArchiveView.as_view(),
        name='by-year'),
   url('^(?P<year>\d{4})/(?P<month>\d{2})/$', views.BlogMonthArchiveView.as_view(),
        name='by-month'),
    url("^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[\w-]+)/$",
        views.BlogDetailView.as_view(), name='detail'),
    url(r'^rss/$', views.RssBlogPostFeed(), name='rss'),
    url(r'^atom/$', views.AtomBlogPostFeed(), name='atom'),
]
