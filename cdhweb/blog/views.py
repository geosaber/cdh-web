from datetime import datetime

from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed
from django.views.generic.detail import DetailView
from django.views.generic.dates import ArchiveIndexView, YearArchiveView, \
    MonthArchiveView

from cdhweb.blog.models import BlogPost
from cdhweb.resources.views import LastModifiedMixin, LastModifiedListMixin


class BlogPostMixinView(object):
    '''View mixin that sets model to Blogpost and returns a
    published BlogPost queryset.'''
    model = BlogPost

    def get_queryset(self):
        # use displayable manager to find published events only
        # (or draft profiles for logged in users with permission to view)
        return BlogPost.objects.published() # TODO: published(for_user=self.request.user)


class BlogPostArchiveMixin(BlogPostMixinView, LastModifiedListMixin):
    '''Mixin with common settings for blogpost archive views'''
    date_field = 'publish_date'
    context_object_name = 'blogposts'
    make_object_list = True
    paginate_by = 12
    template_name = 'blog/blogpost_archive.html'


class BlogIndexView(BlogPostArchiveMixin, ArchiveIndexView):
    date_list_period = 'month'


class BlogYearArchiveView(BlogPostArchiveMixin, YearArchiveView):
    def get_context_data(self, *args, **kwargs):
        context = super(BlogYearArchiveView, self).get_context_data(*args, **kwargs)
        context.update({
            'date_list': BlogPost.objects.dates('publish_date', 'month', order='DESC'),
            'title': self.kwargs['year']
        })
        return context


class BlogMonthArchiveView(BlogPostArchiveMixin, MonthArchiveView):
    month_format = '%m'

    def get_context_data(self, *args, **kwargs):
        context = super(BlogMonthArchiveView, self).get_context_data(*args, **kwargs)
        # current requested month/year for display
        date = datetime.strptime('%(year)s %(month)s' % self.kwargs, '%Y %m')
        context.update({
            'date_list': BlogPost.objects.dates('publish_date', 'month', order='DESC'),
            'title': date.strftime('%B %Y')
        })
        return context


class BlogDetailView(BlogPostMixinView, DetailView, LastModifiedMixin):

    def get_context_data(self, *args, **kwargs):
        context = super(BlogDetailView, self).get_context_data(*args, **kwargs)
        # also set object as page for common page display functionality
        context['page'] = self.object
        return context


class RssBlogPostFeed(Feed):
    title = "Center for Digit Humanities @ Princeton University Updates"
    link = "/updates/"
    description = "Updates and news on work from the Center for Digital Humanities @ Princeton University"

    def items(self):
        return BlogPost.objects.order_by('-publish_date')[:10]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.content


class AtomBlogPostFeed(RssBlogPostFeed):
    feed_type = Atom1Feed
    subtitle = RssBlogPostFeed.description
