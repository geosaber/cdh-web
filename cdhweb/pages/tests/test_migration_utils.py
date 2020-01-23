import json
from datetime import datetime

from django.apps import apps
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from wagtail.core.models import Page, PageRevision

from cdhweb.pages.migration_utils import add_child, create_revision, get_parent
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


class TestCreateRevision(TestCase):
    fixtures = ['sample_pages']

    def test_create(self):
        # create some empty revisions of the homepage
        home = Page.objects.get(title='Home')
        rev1 = create_revision(apps, home)
        self.assertEqual(home.revisions.count(), 1) # now has 1 revision
        rev2 = create_revision(apps, home)
        self.assertEqual(home.revisions.count(), 2) # now 2 revisions
        self.assertEqual(home.latest_revision_created_at, rev2.created_at)

    def test_update_page(self):
        # check that the page associated with the revision is updated
        home = Page.objects.get(title='Home')
        revision = create_revision(apps, home)
        self.assertEqual(home.latest_revision_created_at, revision.created_at)
        self.assertTrue(home.has_unpublished_changes)

    def test_user(self):
        # check creating a revision associated with an arbitrary user
        research = Page.objects.get(title='Research')
        bob = User.objects.create_user('bob', 'bob@example.com', 'password')
        create_revision(apps, research, user=bob)
        revision = research.get_latest_revision()
        self.assertEqual(revision.user, bob)

    def test_timestamp(self):
        # check creating a revision with an arbitrary creation date
        research = Page.objects.get(title='Research')
        old_date = datetime(1991, 12, 1)
        revision = create_revision(apps, research, created_at=old_date)
        self.assertEqual(research.latest_revision_created_at, old_date)

    def test_logging(self):
        # check that the newly created revision is logged
        pass

    def test_content(self):
        # check that the provided page content is included in the revision
        # NOTE the actual fields that store page content (in this case 'body')
        # are usually defined on the model that inherits `Page`, not `Page`!
        research = Page.objects.get(title='Research')
        content = []
        create_revision(apps, research, body=json.dumps(content))
        revision = research.get_latest_revision_as_page()
        self.assertEqual(revision.body, content)
        pass

