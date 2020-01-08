from django.apps import apps
from django.test import TestCase
from django.db.migrations.executor import MigrationExecutor
from django.db import connection

def get_parent(apps, page):
    '''Find the parent of a wagtail page using its `path` attribute.'''
    # see for an explanation of django-treebeard & the `path` attribute:
    # http://www.agilosoftware.com/blog/django-treebard-and-wagtail-page-creation/
    Page = apps.get_model('wagtailcore', 'Page')
    return Page.objects.get(path=page.path[:4])


# migration test case adapted from
# https://www.caktusgroup.com/blog/2016/02/02/writing-unit-tests-django-migrations/
# and from winthrop-django
class TestMigrations(TestCase):

    app = None
    migrate_from = None
    migrate_to = None

    def setUp(self):
        assert self.migrate_from and self.migrate_to, \
            "TestCase '{}' must define migrate_from and migrate_to properties".format(type(self).__name__)
        self.migrate_from = [(self.app, self.migrate_from)]
        self.migrate_to = [(self.app, self.migrate_to)]
        executor = MigrationExecutor(connection)
        old_apps = executor.loader.project_state(self.migrate_from).apps

        # Reverse to the original migration
        executor.migrate(self.migrate_from)
        self.setUpBeforeMigration(old_apps)

        # Run the migration to test
        executor.loader.build_graph()  # reload.
        executor.migrate(self.migrate_to)

        self.apps = executor.loader.project_state(self.migrate_to).apps

    def setUpBeforeMigration(self, apps):
        pass


class TestCreateHomepage(TestMigrations):

    app = 'cdhweb.pages'
    migrate_from = '0001_initial'
    migrate_to = '0002_homepage'

    def test_new_homepage(self):
        # should create one new HomePage
        HomePage = self.apps.get_model('cdhweb.pages', 'HomePage')
        self.assertEqual(HomePage.objects.count(), 1)

    def test_homepage_at_root(self):
        # new HomePage should be located at root
        HomePage = self.apps.get_model('cdhweb.pages', 'HomePage')
        home = HomePage.objects.first()
        parent = get_parent(apps, home)
        self.assertEqual(parent.title, 'Root')

    def test_delete_welcome_page(self):
        # should delete wagtail default welcome page
        Page = self.apps.get_model('wagtailcore', 'Page')
        with self.assertRaises(Page.DoesNotExist):
            Page.objects.get(title='Welcome to your new Wagtail site!')


class TestMigrateHomepage(TestMigrations):

    app = 'cdhweb.pages'
    migrate_from = '0001_initial'
    migrate_to = '0002_homepage'

    def setUpBeforeMigration(self, apps):
        # create a mezzanine home page with content
        pass

    def test_migrate_homepage(self):
        # new HomePage should have migrated mezzanine content
        pass


class TestCreateSite(TestMigrations):

    app = 'cdhweb.pages'
    migrate_from = '0001_initial'
    migrate_to = '0002_homepage'

    def test_create_site(self):
        pass
