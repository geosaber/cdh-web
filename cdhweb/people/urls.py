from django.conf.urls import url

from cdhweb.people import views


urlpatterns = [
    # for now, no generic people list page exists
    # url('^$', views.ProfileListView.as_view(), name='list'),
    url('^staff/$', views.StaffListView.as_view(), name='staff'),
    url('^(?P<slug>[\w-]+)/$', views.ProfileDetailView.as_view(), name='profile'),
]