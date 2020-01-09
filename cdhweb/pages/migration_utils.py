from django.test import TestCase
from django.db.migrations.executor import MigrationExecutor
from django.db import connection


# see for an explanation of django-treebeard & the `path` attribute:
# http://www.agilosoftware.com/blog/django-treebard-and-wagtail-page-creation/
def get_parent(apps, page):
    '''Find the parent of a wagtail page instance. Always returns the underlying
    :class:`wagtail.core.models.Page` rather than a subclass.'''
    # if the path is 4 digits, we're at the root, so there is no parent
    if len(page.path) == 4:
        return None

    # otherwise remove the final 4 digits to get the parent's id (pk)
    Page = apps.get_model('wagtailcore', 'Page')
    return Page.objects.get(path=page.path[:-4])

# add_child utility method adapted from:
# http://www.agilosoftware.com/blog/django-treebard-and-wagtail-page-creation/
def add_child(apps, parent_page, klass, **kwargs):
    '''Create a new draft wagtail page of type klass as a child of page instance
    parent_page, passing along kwargs to its create() function.'''

    # add/set the correct content type for the new page
    ContentType = apps.get_model('contenttypes.ContentType')
    page_content_type = ContentType.objects.get_or_create(
        model=klass.__name__.lower(),
        app_label=klass._meta.app_label,
    )[0]

    # create the new page
    created_page = klass.objects.create(
        content_type=page_content_type,
        path='%s%04d' % (parent_page.path, parent_page.numchild + 1),
        depth=parent_page.depth + 1,
        numchild=0,
        live=False, # create as a draft so that URL is set correctly on publish
        **kwargs
    )

    # update the parent's child count
    parent_page.numchild += 1
    parent_page.save()

    return created_page

# adapted from `copy_page_data_to_content_streamfield`:
# https://www.caktusgroup.com/blog/2019/09/12/wagtail-data-migrations/
def html_to_streamfield(html):
    # create and save a new RichTextBlock with the html content
    # generate JSON referencing the block to store as a page's streamfield
    return [
        {'type': 'body', 'value': [

        ]}
    ]

# adapted from `copy_page_data_to_content_streamfield`:
# https://www.caktusgroup.com/blog/2019/09/12/wagtail-data-migrations/
def create_revision(page, content):
    # create the revision object
    revision = {
        'fields': {
            'approved_go_live_at': None, # needs to become json null
            # 'content_json': json.dumps(content),
            # 'created_at': date, # current timestamp, or pass in?
            'page': page.id,
            'submitted_for_moderation': False,
            # 'user': admin # get admin user or pass in?
        }
    }
    # add the new revision to the page and return it
    return page

# adapted from `TestMigrations`
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