import datetime

from django.http import HttpResponse
from django.views.generic.base import RedirectView
from django.views.generic.dates import ArchiveIndexView, YearArchiveView
from django.views.generic.detail import DetailView
from django.shortcuts import get_object_or_404
from django.utils import timezone
import icalendar

from cdhweb.events.models import Event
from cdhweb.resources.views import LastModifiedMixin, LastModifiedListMixin


class EventMixinView(object):
    '''View mixin that sets model to Event and returns a
    published Event queryset.'''
    model = Event

    def get_queryset(self):
        # use displayable manager to find published events only
        # (or draft profiles for logged in users with permission to view)
        return Event.objects.published() # TODO: published(for_user=self.request.user)


class EventSemesterDates(object):

    def get_semester_date_list(self):
        date_list = []
        dates = Event.objects.dates('start_time', 'month', order='ASC')
        for date in dates:
            # determine semester based on the month
            if date.month <= 5:
                semester = 'Spring'
            elif date.month <= 8:
                semester = 'Summer'
            else:
                semester = 'Fall'

            # add semester + year to list if not already present
            sem_date = (semester, date.year)
            if sem_date not in date_list:
                date_list.append(sem_date)

        return date_list


class UpcomingEventsView(EventMixinView, ArchiveIndexView, EventSemesterDates,
                         LastModifiedListMixin):
    date_field = "start_time"
    allow_future = True
    context_object_name = 'events'

    # NOTE: can't use get_queryset to restrict to upcoming because
    # that affects the archive date list as well; restricting to upcoming
    # events in get_context_data instaed
    def get_context_data(self, *args, **kwargs):
        context = super(UpcomingEventsView, self).get_context_data(*args, **kwargs)
        context.update({
            'events': context['events'].upcoming(),
            'date_list': self.get_semester_date_list()
        })
        return context

    def last_modified(self):
        return self.get_queryset().upcoming() \
            .order_by('updated').first().updated


class EventSemesterArchiveView(EventMixinView, YearArchiveView,
                               EventSemesterDates, LastModifiedListMixin):
    date_field = "start_time"
    make_object_list = True
    allow_future = True
    template_name = 'events/event_archive.html'
    context_object_name = 'events'
    date_list_period = 'month'

    # use month/year archive on the blog and then collapse
    semester_dates = {
        # spring: jan 1 - may 31
        'spring': {'start': (1, 1), 'end': (5, 31)},
        # summer: june 1 - aug 31
        'summer': {'start': (6, 1), 'end': (8, 31)},
        # fall: sep 1 -  dec 31
        'fall': {'start': (9, 1), 'end': (12, 31)},
    }

    def get_dated_items(self):
        date_list, items, context = \
            super(EventSemesterArchiveView, self).get_dated_items()

        # year archive gets items by years; filter by semester
        semester = self.kwargs['semester']
        # generate dates for start and end with current year
        month, year = self.semester_dates[semester]['start']
        start = datetime.datetime(int(self.kwargs['year']), month, year,
            tzinfo=timezone.get_default_timezone())
        month, year = self.semester_dates[semester]['end']
        end = datetime.datetime(int(self.kwargs['year']), month, year,
            tzinfo=timezone.get_default_timezone())
        items = items.filter(start_time__gte=start, start_time__lte=end)

        return (date_list, items, context)

    def get_date_list(self, *args, **kwargs):
        return self.get_semester_date_list()

    def get_context_data(self, *args, **kwargs):
        context = super(EventSemesterArchiveView, self).get_context_data(*args, **kwargs)
        context.update({
            'title': '%s %s' % (self.kwargs['semester'].title(),
                                self.kwargs['year'])
        })
        return context


class EventDetailView(EventMixinView, DetailView, LastModifiedMixin):

    def get_context_data(self, *args, **kwargs):
        context = super(EventDetailView, self).get_context_data(*args, **kwargs)
        # also set object as page for common page display functionality
        context['page'] = self.object
        return context


class EventRedirectView(RedirectView):
    '''Redirect from CDH website v1.0 pk-based urls to new date + slug urls'''
    permanent = True
    query_string = False

    def get_redirect_url(self, *args, **kwargs):
        event = get_object_or_404(Event, pk=kwargs['pk'])
        return event.get_absolute_url()


class EventIcalView(EventDetailView):

    def render_to_response(self, context, **response_kwargs):
        cal = icalendar.Calendar()
        cal.add_component(self.object.ical_event())
        response = HttpResponse(cal.to_ical(), content_type="text/calendar")
        response['Content-Disposition'] = 'attachment; filename="%s.ics"' \
            % self.object.slug
        return response


# ical calendar for all upcoming events
# TODO when we can get to it
# class IcalCalendarView(EventListView):

#     def get_queryset(self):
#         return super(IcalCalendarView, self).get_queryset().upcoming()

#     def render_to_response(self, context, **response_kwargs):
#         cal = icalendar.Calendar()
#         # TODO: required to be compliant
#         # cal.add('prodid', '-//My calendar product//mxm.dk//')
#         # cal.add('version', '2.0')
#         for event in self.get_queryset():
#             cal.add_component(event.ical_event())
#         # TODO: should support cancelled events if possible
#         response = HttpResponse(cal.to_ical(), content_type="text/calendar")
#         response['Content-Disposition'] = 'attachment; filename="CDH-calendar.ics"'
#         return response

