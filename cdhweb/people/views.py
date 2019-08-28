from django.conf import settings
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.urls import reverse

from cdhweb.people.models import Profile
from cdhweb.blog.models import BlogPost
from cdhweb.resources.views import LastModifiedMixin, LastModifiedListMixin
from cdhweb.resources.utils import absolutize_url


class ProfileMixinView(object):
    '''Profile view mixin that sets model to Profile and returns a
    published Profile queryset.'''

    model = Profile

    def get_queryset(self):
        # use displayable manager to find published profiles only
        # (or draft profiles for logged in users with permission to view)
        return Profile.objects.published() # TODO: published(for_user=self.request.user)


class ProfileDetailView(ProfileMixinView, DetailView, LastModifiedMixin):

    def get_queryset(self):
        # only published profiles with staff flag get a detail page
        return super().get_queryset().staff()

    def get_context_data(self, *args, **kwargs):
        context = super(ProfileDetailView, self).get_context_data(*args, **kwargs)

        # retrieve 3 most recent published blog posts with the current user as author
        recent_posts = BlogPost.objects.filter(users__id=self.object.user.id).published()[:3]

        # also set object as page for common page display functionality
        context.update({
            'page': self.object,
            'opengraph_type': 'profile',
            'recent_posts': recent_posts,
        })
        if self.object.thumb:
            context['preview_image'] = absolutize_url(''.join([settings.MEDIA_URL,
                str(self.object.thumb)]))

        return context


class ProfileListView(ProfileMixinView, ListView, LastModifiedListMixin):
    '''Base class for profile list views'''

    #: title for this category of people
    page_title = ''
    #: title for non-past people in this category of people
    current_title = ''
    #: label for past people in this category of people
    past_title = ''
    #: show CDH position on profile card (true by default)
    show_cdh_position = True
    #: show grant recepient information on profle card (true by default)
    show_grant = True
    #: show official job title (false by default)
    show_job_title = False
    #: show departmental or instutional affiliation (false by default)
    show_affiliation = False
    #: show related events (i.e. for speakers)
    show_events = False

    def get_queryset(self):
        # get published profile ordered by position (job title then start date)
        return super().get_queryset().order_by_position().distinct()

    def get_current_profiles(self):
        '''Get current profiles from the queryset. Override to customize
        which filter is used. By default, uses generic current logic that
        checks both positions and grants.'''
        return self.object_list.current()

    def get_past_profiles(self):
        '''Get past profiles. Override to customize filters and ordering. By
        default, assumes any profiles that aren't current are past.'''
        current = self.get_current_profiles()
        return self.object_list.exclude(id__in=current.values('id'))

    def get_context_data(self):
        context = super().get_context_data()
        # update context to display current and past people separately
        current = self.get_current_profiles()
        # filter past based current ids, rather than trying to do the complicated
        # query to find not current people
        past = self.get_past_profiles()
        context.update({
            'current': current,
            'past': past,
            'title': self.page_title,
            'past_title': self.past_title,
            'current_title': self.current_title or self.page_title, # use main title as default
            'archive_nav_urls': [
                ('Staff', reverse('people:staff')),
                ('Postdoctoral Fellows', reverse('people:postdocs')),
                ('Students', reverse('people:students')),
                ('Faculty Affiliates', reverse('people:faculty')),
                ('Executive Committee', reverse('people:exec-committee')),
                ('Speakers', reverse('people:speakers')),
            ],
            # flags for profile card display
            'show_cdh_position': self.show_cdh_position,
            'show_grant': self.show_grant,
            'show_job_title': self.show_job_title,
            'show_affiliation': self.show_affiliation,
            'show_events': self.show_events
        })
        return context


class StaffListView(ProfileListView):
    '''Display current and past CDH staff'''
    page_title = 'Staff'
    past_title = 'Past Staff'
    # don't show grant recipient info
    show_grant = False

    def get_queryset(self):
        # filter to profiles with staff flag set and exclude postdocs
        # and students
        # (already ordered by job title sort order and then by last name)
        return super().get_queryset().staff().not_postdocs().not_students()
        # NOTE: this won't filter correctly if we ever have someone who
        # goes from a postdoc or student role to a staff position, however
        # filtering only on current role messes up past staff

    def get_current_profiles(self):
        # we only care about current position, grant doesn't matter;
        # filter out past faculty directors who are current exec members
        return self.object_list.current_position_nonexec()


class PostdocListView(ProfileListView):
    '''Display current and past postdoctoral fellows'''
    page_title = 'Postdoctoral Fellows'
    past_title = 'Past Postdoctoral Fellows'
    show_grant = False

    def get_queryset(self):
        # filter to just postdocs
        return super().get_queryset().postdocs()

    def get_current_profiles(self):
        # we only care about current position, grant doesn't matter
        return self.object_list.current_position()

    def get_past_profiles(self):
        # show most recent first
        return super().get_past_profiles()\
            .order_by('-user__positions__end_date')


class StudentListView(ProfileListView):
    '''Display current and past graduate fellows, graduate and undergraduate
    assistants.'''
    page_title = 'Students'
    past_title = 'Alumni'

    def get_queryset(self):
        # filter to just students
        return super().get_queryset().student_affiliates() \
            .grant_years().project_manager_years()

    def get_past_profiles(self):
        # show most recent first
        return super().get_past_profiles()\
            .order_by('-user__positions__end_date')

    # def get_past_profiles(self):
    #     return super().get_past_profiles.order_by()


class FacultyListView(ProfileListView):
    '''Display current and past faculty affiliates'''
    page_title = 'Faculty Affiliates'
    past_title = 'Past {}'.format(page_title)
    #: do not show person positions; want grant information instead
    show_cdh_position = False

    def get_queryset(self):
        # filter to faculty affiliates, annotate with grant years, and order by
        # name
        return super().get_queryset().faculty_affiliates().grant_years() \
                      .order_by('user__last_name')

    def get_current_profiles(self):
        # we only care about current grants, position doesn't matter
        return self.object_list.current_grant()


class ExecListView(ProfileListView):
    '''Display current and past executive committee members.'''
    page_title = 'Executive Committee'
    past_title = 'Past members of {}'.format(page_title)
    #: do not CDH positions or grants; show job title
    show_cdh_position = False
    show_grant = False
    show_job_title = True

    def get_queryset(self):
        # filter to exec members
        return super().get_queryset().executive_committee().order_by('user__last_name')

    def get_current_profiles(self):
        # we only care about current position, grant doesn't matter
        return self.object_list.current_position()

    def get_context_data(self):
        context = super().get_context_data()
        # executive committee needs an additional filter:
        # exec members, sits with committee, then alumni as usual
        current = context['current']
        context.update({
            'current': current.exec_member(),
            'sits_with': current.sits_with_exec(),
        })
        return context


class SpeakerListView(ProfileListView):
    '''Display upcoming and past speakers.'''
    page_title = 'Speakers'
    current_title = 'Upcoming {}'.format(page_title)
    past_title = 'Past {}'.format(page_title)
    #: show affiliation and info about events
    show_affiliation = True
    show_events = True
    # don't show non-speaker related info (shouldn't happen)
    show_grant = False
    show_cdh_position = False

    def get_queryset(self):
        # filter to just speakers
        return super().get_queryset().speakers()

    def get_current_profiles(self):
        # return only speakers with upcoming events, sorted by recent event
        return self.object_list.has_upcoming_events().order_by_event()

    def get_past_profiles(self):
        # resort the past profiles and show latest first
        return super().get_past_profiles().order_by_event().reverse()
