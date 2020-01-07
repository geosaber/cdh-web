# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

# add_child utility method taken from:
# http://www.agilosoftware.com/blog/django-treebard-and-wagtail-page-creation/
def add_child(apps, parent_page, klass, **kwargs):

    ContentType = apps.get_model('contenttypes.ContentType')

    page_content_type = ContentType.objects.get_or_create(
        model=klass.__name__.lower(),
        app_label=klass._meta.app_label,
    )[0]

    url_path = '%s%s/' % (parent_page.url_path, kwargs.get('slug'))

    created_page = klass.objects.create(
        content_type=page_content_type,
        path='%s00%02d' % (parent_page.path, parent_page.numchild + 1),
        depth=parent_page.depth + 1,
        numchild=0,
        url_path=url_path,
        **kwargs
    )

    parent_page.numchild += 1
    parent_page.save()

    return created_page

def create_homepage(apps, schema_editor):
    '''Search for an existing mezzanine Page for the home page, if any, and save
    its content. Create a new wagtail HomePage using this content and set the
    site's root to the new homepage. Delete the default wagtail welcome page,
    if it exists.'''

    # MezzaninePage = apps.get_model('mezzanine.pages', 'Page')
    Page = apps.get_model('wagtailcore', 'Page')
    HomePage = apps.get_model('cdhweb.pages', 'HomePage')

    # try:
    #     old_home = Page.objects.get(title='Home')
    #     content = old_home.richtextpage.content
    # except (Page.DoesNotExist, AttributeError):
    #     content = ''

    root = Page.objects.get(title='Root')
    new_home = add_child(apps, root, HomePage, title='Home')
    # new_home.save_revision().publish() # create a new revision and publish

    welcome = Page.objects.get(title='Welcome to your new Wagtail site!')
    welcome.delete() # delete welcome page


def revert_create_homepage(apps, schema_editor):
    '''Delete the created wagtail HomePage and replace with a placeholder
    welcome page.'''

    Page = apps.get_model('wagtailcore', 'Page')
    HomePage = apps.get_model('cdhweb.pages', 'HomePage')
    
    root = Page.objects.get(title='Root')
    add_child(apps, root, Page, title='Welcome to your new Wagtail site!')

    HomePage.objects.first().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('cdhweb.pages', '0001_initial')
    ]

    operations = [
        migrations.RunPython(create_homepage, reverse_code=revert_create_homepage)
    ]