from datetime import datetime

from django.test import TestCase
from django.urls import resolve, reverse
from django.utils.html import escape

from cdhweb.blog.models import BlogPost
from cdhweb.blog.views import RssBlogPostFeed


class TestBlog(TestCase):

    def test_get_absolute_url(self):
        jan15 = datetime(2016, 1, 15)
        post = BlogPost(publish_date=jan15, slug='news-and-updates')
        # single-digit months should be converted to two-digit for url
        resolved_url = resolve(post.get_absolute_url())
        assert resolved_url.namespace == 'blog'
        assert resolved_url.url_name == 'detail'
        assert resolved_url.kwargs['year'] == str(post.publish_date.year)
        assert resolved_url.kwargs['month'] == '%02d' % post.publish_date.month
        assert resolved_url.kwargs['slug'] == post.slug


class TestViews(TestCase):
    fixtures = ['test_blogposts.json']

    def test_rss_feed(self):
        post = BlogPost.objects.first()

        response = self.client.get(reverse('blog:rss'))
        assert response['content-type'] == 'application/rss+xml; charset=utf-8'
        self.assertContains(response, RssBlogPostFeed.title)
        self.assertContains(response, RssBlogPostFeed.description)
        # check for post content
        self.assertContains(response, post.title)
        self.assertContains(response, post.get_absolute_url())
        self.assertContains(response, escape(post.content[:100]))

    def test_atom_feed(self):
        response = self.client.get(reverse('blog:atom'))
        assert response['content-type'] == 'application/atom+xml; charset=utf-8'
        self.assertContains(response, RssBlogPostFeed.title)
        self.assertContains(response, RssBlogPostFeed.description)

    def test_index(self):
        response = self.client.get(reverse('blog:list'))

        # title displays
        self.assertContains(response, 'Latest Updates')

        for post in BlogPost.objects.all():
            self.assertContains(response, post.title)
            self.assertContains(response, post.get_absolute_url())
            self.assertContains(response, post.description)
            for auth in post.users.all():
                self.assertContains(response, str(auth))

            # links to blog archive by montth
            self.assertContains(response,
                reverse('blog:by-month', kwargs={'year': post.publish_date.year,
                        'month': post.publish_date.strftime('%m')}))

        # feed links should occur twice: once in header, once in body
        self.assertContains(response, reverse('blog:rss'), count=2)
        self.assertContains(response, reverse('blog:atom'), count=2)

    def test_blogpost_detail(self):
        post = BlogPost.objects.first()
        response = self.client.get(post.get_absolute_url())

        self.assertContains(response, post.title)
        self.assertContains(response, post.get_absolute_url())
        self.assertContains(response, post.description)
        for auth in post.users.all():
            self.assertContains(response, str(auth))

        self.assertContains(response, ', '.join(post.keywords.all()))

        # keywords & description in header
        self.assertContains(response,
            '<meta name="keywords" content="%s"/>' % ', '.join(post.keywords.all()))
        self.assertContains(response,
            '<meta name="description" content="%s"/>' % post.description)


        # feed links should occur twice: once in header, once in body
        self.assertContains(response, reverse('blog:rss'), count=2)
        self.assertContains(response, reverse('blog:atom'), count=2)

    def test_blogs_by_year(self):
        response = self.client.get(reverse('blog:by-year', kwargs={'year': 2017}))

        assert response.context['title'] == '2017'
        # date-specific title displays
        self.assertContains(response, '2017 Updates')
        # links to blog archive by montth
        self.assertContains(response,
            reverse('blog:by-month', kwargs={'year': 2017, 'month': '09'}))

        # date filtering is really django logic, this is just
        # a sanity check for display
        for post in BlogPost.objects.filter(publish_date__year=2017):
            self.assertContains(response, post.title)
            self.assertContains(response, post.get_absolute_url())

        for post in BlogPost.objects.exclude(publish_date__year=2017):
            self.assertNotContains(response, post.title)
            self.assertNotContains(response, post.get_absolute_url())

    def test_blogs_by_month(self):
        response = self.client.get(reverse('blog:by-month',
            kwargs={'year': 2017, 'month': '09'}))

        assert response.context['title'] == 'September 2017'
        # date-specific title displays
        self.assertContains(response, 'September 2017 Updates')

        # date filtering is really django logic, this is just
        # a sanity check for display
        for post in BlogPost.objects.filter(publish_date__year=2017,
                                            publish_date__month=9):
            self.assertContains(response, post.title)
            self.assertContains(response, post.get_absolute_url())

        for post in BlogPost.objects.exclude(publish_date__year=2017,
                                             publish_date__month=9):
            self.assertNotContains(response, post.title)
            self.assertNotContains(response, post.get_absolute_url())


