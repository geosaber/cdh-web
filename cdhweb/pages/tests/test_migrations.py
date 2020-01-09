from django.apps import apps

from cdhweb.pages.migration_utils import TestMigrations, get_parent


class TestCreateHomepage(TestMigrations):

    app = 'cdhpages'
    migrate_from = '0001_initial'
    migrate_to = '0002_homepage'

    def test_new_homepage(self):
        # should create one new HomePage
        HomePage = self.apps.get_model('cdhpages', 'HomePage')
        self.assertEqual(HomePage.objects.count(), 1)

    def test_homepage_at_root(self):
        # new HomePage should be located at root
        HomePage = self.apps.get_model('cdhpages', 'HomePage')
        home = HomePage.objects.first()
        parent = get_parent(apps, home)
        self.assertEqual(parent.title, 'Root')

    def test_delete_welcome_page(self):
        # should delete wagtail default welcome page
        Page = self.apps.get_model('wagtailcore', 'Page')
        with self.assertRaises(Page.DoesNotExist):
            Page.objects.get(title='Welcome to your new Wagtail site!')

    def test_site_root_page(self):
        # default site should point to new home page
        Site = apps.get_model('wagtailcore', 'Site')
        HomePage = self.apps.get_model('cdhpages', 'HomePage')
        home = HomePage.objects.first()
        site = Site.objects.first()
        self.assertEqual(site.root_page_id, home.id)


class TestMigrateHomepage(TestMigrations):

    app = 'cdhpages'
    migrate_from = '0001_initial'
    migrate_to = '0002_homepage'

    def setUpBeforeMigration(self, apps):
        # create a mezzanine home page with content
        pass

    def test_migrate_homepage(self):
        # new HomePage should have migrated mezzanine content
        pass
