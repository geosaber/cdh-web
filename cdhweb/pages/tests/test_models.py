from django.test import SimpleTestCase
from wagtail.core.models import Page
from wagtail.tests.utils import WagtailPageTests
from wagtail.tests.utils.form_data import (nested_form_data, rich_text,
                                           streamfield)

from cdhweb.pages.models import (ContentPage, HomePage, LandingPage,
                                 LinkableSectionBlock)


class TestLinkableSectionBlock(SimpleTestCase):

    def test_clean(self):
        block = LinkableSectionBlock()
        cleaned_values = block.clean({'anchor_text': 'Working at the CDH'})
        assert cleaned_values['anchor_text'] == 'working-at-the-cdh'

    def test_render(self):
        block = LinkableSectionBlock()
        html = block.render(block.to_python({
            'title': 'Working at the CDH',
            'body': 'Info about how to get a job working at the CDH',
            'anchor_text': 'working-at-the-cdh',
        }))
        expected_html = '''
            <div id="working-at-the-cdh">
            <h2>Working at the CDH
            <a class="headerlink" href="#working-at-the-cdh"
               title="Permalink to this section">¶</a>
            </h2>
            <div class="rich-text">
                Info about how to get a job working at the CDH
            </div>
            </div>
        '''

        self.assertHTMLEqual(html, expected_html)


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
