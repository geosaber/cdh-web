from django.test import SimpleTestCase
from wagtail.core.models import Page
from wagtail.tests.utils import WagtailPageTests
from wagtail.tests.utils.form_data import (nested_form_data, rich_text,
                                           streamfield)

from cdhweb.pages.models import ContentPage, HomePage, LandingPage


class TestHomePage(WagtailPageTests):
    
    def test_can_create(self):
        root = Page.objects.get(title='Root')
        self.assertCanCreate(root, HomePage, nested_form_data({
            'title': 'Home 2',
            'slug': 'home-2',
            'body': streamfield([
                ('paragraph', rich_text('homepage body text')),
            ]),
        }))

    def test_parent_pages(self):
        # only allowed parent is basic page (root)
        self.assertAllowedParentPageTypes(HomePage, [Page])

    def test_subpages(self):
        # landing pages or content pages can be children
        self.assertAllowedSubpageTypes(HomePage, [LandingPage, ContentPage])

    def test_template(self):
        pass


class TestLandingPage(WagtailPageTests):
    
    def test_can_create(self):
        pass

    def test_parent_pages(self):
        # only allowed parent is home
        self.assertAllowedParentPageTypes(LandingPage, [HomePage])

    def test_subpages(self):
        # only allowed child is content page
        self.assertAllowedSubpageTypes(LandingPage, [ContentPage])

    def test_template(self):
        pass


class TestContentPage(WagtailPageTests):
    
    def test_can_create(self):
        pass

    def test_parent_pages(self):
        # can be child of home, landing page, or another content page
        self.assertAllowedParentPageTypes(ContentPage,
                                          [HomePage, LandingPage, ContentPage])

    def test_subpages(self):
        # only allowed child is content page
        self.assertAllowedSubpageTypes(ContentPage, [ContentPage])

    def test_template(self):
        pass
