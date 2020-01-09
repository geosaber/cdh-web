from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from wagtail.core.models import Page, PageRevision

from cdhweb.pages.migration_utils import add_child, get_parent, create_revision
from cdhweb.pages.models import ContentPage, HomePage


class TestGetParent(TestCase):
    fixtures = ['sample_pages']

    def test_root(self):
        # should return None for root since it has no parent
        root = Page.objects.get(title='Root')
        self.assertIsNone(get_parent(apps, root))

    def test_single_parent(self):
        # should return root for first-level node
        root = Page.objects.get(title='Root')
        home = Page.objects.get(title='Home')
        self.assertEqual(get_parent(apps, home), root)

    def test_nested(self):
        # should return immediate parent for nested node
        home = Page.objects.get(title='Home')
        research = Page.objects.get(title='Research')
        self.assertEqual(get_parent(apps, research), home)


class TestAddChild(TestCase):
    fixtures = ['sample_pages']

    def test_add_at_root(self):
        # should add at the root with correct props and update root child count
        root = Page.objects.get(title='Root')
        home_type = ContentType.objects.get(model='homepage')
        add_child(apps, root, HomePage, title='New Home')
        new_home = HomePage.objects.get(title='New Home')

        self.assertEqual(HomePage.objects.count(), 2)  # added second homepage
        self.assertEqual(new_home.content_type, home_type)  # correct type
        self.assertEqual(new_home.live, False)  # is draft
        self.assertEqual(new_home.numchild, 0)  # no children yet
        self.assertEqual(new_home.path, '00010002')  # correct path
        self.assertEqual(new_home.title, 'New Home')  # passed kwarg
        self.assertEqual(new_home.get_parent(), root)  # correct parent
        self.assertEqual(root.numchild, 2)  # root has 2 children

    def test_add_nested(self):
        # should add nested with correct props and update parent child count
        research = Page.objects.get(title='Research')
        cp_type = ContentType.objects.get(model='contentpage')
        add_child(apps, research, ContentPage, title='CDH Software')
        software = ContentPage.objects.get(title='CDH Software')

        self.assertEqual(software.content_type, cp_type)  # correct type
        self.assertEqual(software.live, False)  # is draft
        self.assertEqual(software.numchild, 0)  # no children yet
        self.assertEqual(software.path, '0001000100010001')  # correct path
        self.assertEqual(software.title, 'CDH Software')  # passed kwarg
        self.assertEqual(software.get_parent(), research)  # correct parent
        self.assertEqual(research.numchild, 1)  # parent has 1 child

    def test_with_kwargs(self):
        pass


def TestCreateRevision(TestCase):
    fixtures = ['sample_pages']

    def test_create(self):
        # create an empty revision of the homepage
        home = Page.objects.get(title='Home')
        revision = create_revision(apps, home)
        self.assertEqual(home.revisions.count(), 1) # now has 1 revision

    def test_update_page(self):
        # check that the page associated with the revision is updated
        home = Page.objects.get(title='Home')
        revision = create_revision(apps, home)
        self.assertEqual(home.latest_revision_created_at, revision.created_at)
        self.assertTrue(home.has_unpublished_changes)

    def test_content(self):
        # check that the provided content is included in the revision
        home = Page.objects.get(title='Home')
        revision = create_revision(apps, home, content=[])
        pass

    def test_user(self):
        pass

    def test_timestamp(self):
        pass

    def test_logging(self):
        pass