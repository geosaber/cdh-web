# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

# add_child utility method adapted from:
# http://www.agilosoftware.com/blog/django-treebard-and-wagtail-page-creation/
def add_child(apps, parent_page, klass, **kwargs):
    '''Create a new draft wagtail page of type klass as a child of page instance
    parent_page, passing along kwargs to its create() function.'''

    ContentType = apps.get_model('contenttypes.ContentType')

    page_content_type = ContentType.objects.get_or_create(
        model=klass.__name__.lower(),
        app_label=klass._meta.app_label,
    )[0]

    created_page = klass.objects.create(
        content_type=page_content_type,
        path='%s00%02d' % (parent_page.path, parent_page.numchild + 1),
        depth=parent_page.depth + 1,
        numchild=0,
        live=False, # create as a draft so that URL is set correctly on publish
        **kwargs
    )

    parent_page.numchild += 1
    parent_page.save()

    return created_page

def create_homepage(apps, schema_editor):
    '''Create a new wagtail HomePage with any existing content from an old
    Mezzanine home page, and delete Wagtail's default welcome page.'''

    RichTextPage = apps.get_model('pages', 'RichTextPage')
    Page = apps.get_model('wagtailcore', 'Page')
    HomePage = apps.get_model('cdhweb.pages', 'HomePage')

    # check for an existing mezzanine 'home' page and save its content
    old_home = RichTextPage.objects.filter(title='Home')
    if old_home.count() == 1:
        content = old_home.first().content

    # create the new homepage underneath site root and publish it
    root = Page.objects.get(title='Root')
    add_child(apps, root, HomePage, title='Home')
    # new_home.save_revision().publish()

    # delete the default welcome page
    welcome = Page.objects.get(title='Welcome to your new Wagtail site!')
    welcome.delete()


def revert_create_homepage(apps, schema_editor):
    '''Delete the created wagtail HomePage and replace with a placeholder
    welcome page.'''
    # NOTE this does not restore deleted mezzanine page!

    Page = apps.get_model('wagtailcore', 'Page')
    HomePage = apps.get_model('cdhweb.pages', 'HomePage')
    
    # create a welcome page, since at least one child of root is required
    root = Page.objects.get(title='Root')
    add_child(apps, root, Page, title='Welcome to your new Wagtail site!')

    # delete the created HomePage
    HomePage.objects.first().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('cdhweb.pages', '0001_initial')
    ]

    operations = [
        migrations.RunPython(create_homepage,
                             reverse_code=revert_create_homepage)
    ]