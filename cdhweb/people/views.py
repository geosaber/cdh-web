from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from cdhweb.people.models import Profile
from cdhweb.resources.views import LastModifiedMixin, LastModifiedListMixin


class ProfileMixinView(object):
    '''Profile view mixin that sets model to Profile and returns a
    published Profile queryset.'''

    model = Profile

    def get_queryset(self):
        # use displayable manager to find published profiles only
        # (or draft profiles for logged in users with permission to view)
        return Profile.objects.published() # TODO: published(for_user=self.request.user)



class ProfileDetailView(ProfileMixinView, DetailView, LastModifiedMixin):

    def get_context_data(self, *args, **kwargs):
        context = super(ProfileDetailView, self).get_context_data(*args, **kwargs)
        # also set object as page for common page display functionality
        context['page'] = self.object
        return context


# class ProfileListView(ProfileMixinView, ListView):
#     # NOTE: we probably don't need a full list of all profiles;
#     # instead we'll probably want a few filtered lists, e.g. current
#     # staff, guest speakers, alumni, etc.
#     pass


class StaffListView(ProfileMixinView, ListView, LastModifiedListMixin):

    def get_queryset(self):
        # order by job title sort order and then by last name
        # (TODO: perhaps job start date for secondary?)
        return super(StaffListView, self).get_queryset() \
            .filter(is_staff=True) \
            .order_by('user__positions__title__sort_order', 'user__last_name')

    def get_context_data(self):
        context = super(StaffListView, self).get_context_data()
        context.update({
            'title': 'Who we are'
        })
        return context



