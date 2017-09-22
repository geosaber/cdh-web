from io import StringIO
import json
import os
from unittest.mock import Mock, patch

from attrdict import AttrMap
import dateutil.parser
from django.contrib.sites.models import Site
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from pucas.ldap import LDAPSearchException
import pytest

from cdhweb.blog.models import BlogPost
from cdhweb.events.models import Event, EventType
from cdhweb.people.models import Person, Title, Position
from cdhweb.projects.models import Project, Role, Membership
from cdhweb.resources.management.commands import import_datav1


FIXTURE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
    '..', 'fixtures')


class TestImportCommand(TestCase):

    test_data = os.path.join(FIXTURE_DIR, 'test_import_data.json')

    def setUp(self):
        self.cmd = import_datav1.Command()
        self.cmd.stdout = StringIO()
        self.cmd.stderr = StringIO()
        self.cmd.current_site = Site.objects.get_current()

    def test_run(self):
        # nonexistent file path
        bad_file_path = '/tmp/not/a/real/file'
        with pytest.raises(CommandError) as err:
            call_command(self.cmd, bad_file_path)
        assert "No such file or directory: '%s'" % bad_file_path in \
            str(err)

        # non-json file path
        bad_file_path = __file__
        with pytest.raises(CommandError) as err:
            call_command(self.cmd, bad_file_path)
        assert "Error parsing JSON" in str(err)

        # modes
        with patch.object(self.cmd, 'import_profiles') as mock_import_profile:
            with patch.object(self.cmd, 'import_events') as mock_import_events:
                # import people only
                call_command(self.cmd, '--people', self.test_data)
                mock_import_events.assert_not_called()
                assert mock_import_profile.call_args
                mock_import_profile.reset_mock()

                # import events only
                call_command(self.cmd, '--events', self.test_data)
                mock_import_profile.assert_not_called()
                assert mock_import_events.call_args
                mock_import_events.reset_mock()

                # no arg, run all imports
                call_command(self.cmd, self.test_data)
                assert mock_import_profile.call_args
                assert mock_import_events.call_args

    @patch('cdhweb.resources.management.commands.import_datav1.user_info_from_ldap')
    def test_init_user(self, mockuserfromldap):
        test_netid = 'foo'
        email = '%s@example.com' % test_netid
        staffdata = Mock()
        self.cmd.init_user(email, staffdata)
        # user should exist
        user = Person.objects.get(username=test_netid)
        assert user
        # ldap init should have been called
        mockuserfromldap.assert_called_with(user)

        # re-init does not recreate
        self.cmd.init_user(email, staffdata)
        assert Person.objects.filter(username=test_netid).count() == 1

        # email alias
        test_netid = 'rebecca.s.koeser'
        email = '%s@example.com' % test_netid
        self.cmd.init_user(email, staffdata)
        # alias should be used rather than email name
        assert Person.objects.get(username=self.cmd.email_aliases[test_netid])

        # simulate ldap exception and set data from import
        mockuserfromldap.side_effect = LDAPSearchException
        test_netid = 'foo'
        email = '%s@example.com' % test_netid
        staffdata.fields.email = email
        first, last = 'Joe G.', 'Smith'
        staffdata.fields.name = ' '.join([first, last])
        self.cmd.init_user(email, staffdata)
        user = Person.objects.get(username=test_netid)
        assert user.email == email
        assert user.first_name == first
        assert user.last_name == last
        assert user.profile
        assert user.profile.title == staffdata.fields.name

    def test_import_profiles(self):
        with open(self.test_data) as datafile:
            data = json.load(datafile)

        # set mock to create and return a user
        def mock_init_user(*args, **kwargs):
            return Person.objects.create(username='claus')

        stafferdata = data[0]['fields']
        pagedata = data[1]['fields']

        with patch.object(self.cmd, 'init_user', new=mock_init_user):
            self.cmd.import_profiles(data)

        # get updated record and check details
        user = Person.objects.get(username='claus')
        assert user.profile
        assert stafferdata['education'] in user.profile.education
        assert user.profile.is_staff
        assert user.profile.site == self.cmd.current_site
        jobtitle = Title.objects.get(title=stafferdata['title'])
        assert jobtitle
        assert Position.objects.get(title=jobtitle, user=user)
        # displayable page data
        assert user.profile.bio == pagedata['extra_content']
        assert user.profile.slug == pagedata['slug']
        assert user.profile.status == pagedata['status']

        assert user.profile.description == pagedata['description']
        assert user.profile.gen_description == pagedata['gen_description']
        assert user.profile.publish_date == \
            dateutil.parser.parse(pagedata['publish_date'])
        assert user.profile.created == \
            dateutil.parser.parse(pagedata['created'])

    def test_set_event_type(self):
        # duplicate setup from command script
        event_type_lookup = {event.name: event for event in EventType.objects.all()}
        item = AttrMap({'fields': {'event_title': ""}})

        event = Event()
        # title includes event type
        item.fields.event_title = "Workshop: Data Visualization"
        self.cmd.set_event_type(event, item, event_type_lookup)
        assert event.event_type.name == 'Workshop'
        assert event.title == 'Data Visualization'
        # title *is* event type
        item.fields.event_title = 'Reading Group'
        self.cmd.set_event_type(event, item, event_type_lookup)
        assert event.event_type.name == 'Reading Group'
        assert event.title == item.fields.event_title
        # partial matches
        item.fields.event_title = 'Fall Open House'
        self.cmd.set_event_type(event, item, event_type_lookup)
        assert event.event_type.name == 'Reception'
        assert event.title == item.fields.event_title
        item.fields.event_title = 'Grad Student Working Group'
        self.cmd.set_event_type(event, item, event_type_lookup)
        assert event.event_type.name == 'Working Group'
        assert event.title == item.fields.event_title
        # fallback - no match, with colon
        item.fields.event_title = "The Future's Future: Augmented Reality"
        self.cmd.set_event_type(event, item, event_type_lookup)
        assert event.event_type.name == 'Guest Lecture'
        assert event.title == item.fields.event_title

    def test_import_events(self):
        with open(self.test_data) as datafile:
            data = json.load(datafile)

        eventdata = data[2]
        pagedata = data[3]['fields']
        self.cmd.import_events(data)
        event = Event.objects.get(pk=eventdata['pk'])
        assert event.event_type.name == 'Reception'
        assert event.content == eventdata['fields']['event_description']
        assert event.start_time == \
             dateutil.parser.parse(eventdata['fields']['event_start_time'])
        assert event.end_time == \
            dateutil.parser.parse(eventdata['fields']['event_end_time'])
        # location in fixture is one of several that maps to CDH
        assert event.location.short_name == 'CDH'
        assert event.site == self.cmd.current_site
        # displayable page data
        assert event.slug == pagedata['slug']
        assert event.status == pagedata['status']
        # description gets regenerated by mezzanine
        # assert event.description == pagedata['description']
        assert event.gen_description == pagedata['gen_description']
        assert event.publish_date == \
            dateutil.parser.parse(pagedata['publish_date'])
        assert event.created == \
            dateutil.parser.parse(pagedata['created'])

    def test_import_blog(self):
        with open(self.test_data) as datafile:
            data = json.load(datafile)

        blogdata = data[4]
        self.cmd.import_blogposts(data)
        post = BlogPost.objects.first()
        copied_fields = ['slug', 'title', 'description', 'gen_description',
            'status', 'in_sitemap', 'content']
        for field in copied_fields:
            assert getattr(post, field) == blogdata['fields'][field]
        assert post.publish_date == \
            dateutil.parser.parse(blogdata['fields']['publish_date'])

        # keywords converted to assigned keywords
        keywords = [kw.keyword.title for kw in post.keywords.all()]
        for term in blogdata['fields']['keywords_string'].split(' '):
            assert term in keywords

    def test_import_project(self):
        with open(self.test_data) as datafile:
            data = json.load(datafile)

        projdata = data[5]
        pagedata = data[6]
        self.cmd.import_projects(data)
        proj = Project.objects.first()
        assert proj.title == projdata['fields']['project_title']
        assert proj.short_description == projdata['fields']['project_subtitle']
        assert proj.long_description == projdata['fields']['project_description']
        assert proj.description == projdata['fields']['project_summary']
        assert proj.gen_description is False

        copied_fields = ['slug', 'title', 'status', 'in_sitemap']
        for field in copied_fields:
            assert getattr(proj, field) == pagedata['fields'][field]
        assert proj.publish_date == \
            dateutil.parser.parse(pagedata['fields']['publish_date'])

        # keywords converted to assigned keywords
        keywords = [kw.keyword.title for kw in proj.keywords.all()]
        for term in pagedata['fields']['keywords_string'].split(' '):
            assert term in keywords

        # check project member import
        member_names = [str(person) for person in proj.members.all()]
        for name in ['Meredith Martin', 'Meagan Wilson', 'Jean Bauer']:
            assert name in member_names

        # placeholder grant created to associate members
        assert proj.grant_set.count() == 1

        assert proj.membership_set.get(user__last_name='Martin').role.title \
            == 'Project Director'
        assert proj.membership_set.get(user__last_name='Bauer').role.title \
            == 'Technical Lead'
        assert proj.membership_set.get(user__last_name='Wilson').role.title \
            == 'Project Manager'






