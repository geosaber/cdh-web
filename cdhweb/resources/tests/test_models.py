from django.test import TestCase

from cdhweb.resources.models import Attachment, ResourceType

class TestAttachment(TestCase):

    def test_str(self):
        attach = Attachment(title='My Document')
        assert str(attach) == attach.title

        attach.attachment_type = 'PDF'
        assert str(attach) == '%s (%s)' % (attach.title, attach.attachment_type)

        attach.author = 'Person'
        assert str(attach) == '%s, %s (%s)' % (attach.title, attach.author,
            attach.attachment_type)

        attach.attachment_type = None
        assert str(attach) == '%s, %s' % (attach.title, attach.author)


class TestResourceType(TestCase):

    def test_str(self):
        restype = ResourceType(name='twitter')