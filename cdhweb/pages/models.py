from random import shuffle

import bleach
from django.db import models
from django.template.defaultfilters import striptags, truncatechars_html
from django.utils.text import slugify
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.core.blocks import (CharBlock, RichTextBlock, StreamBlock,
                                 StructBlock, TextBlock)
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Page
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index

from cdhweb.blog.models import BlogPost
from cdhweb.events.models import Event
from cdhweb.projects.models import Project

#: commonly allowed tags for RichTextBlocks
RICH_TEXT_TAGS = ['h3', 'h4', 'bold', 'italic', 'link', 'ol', 'ul', 'blockquote']

#: help text for image alternative text
ALT_TEXT_HELP = """Alternative text for visually impaired users to
briefly communicate the intended message of the image in this context."""


class PagePreviewDescriptionMixin(models.Model):
    '''Page mixin with logic for page preview content. Adds an optional
    richtext description field, and methods to get description and plain-text
    description, for use in previews on the site and plain-text metadata
    previews.'''

    # adapted from PPA; does not allow <p> tags in description
    #: brief description for preview display
    description = RichTextField(
        blank=True, features=['bold', 'italic'],
        help_text='Optional. Brief description for preview display. Will ' +
        'also be used for search description (without tags), if one is ' +
        'not entered.')
    #: maximum length for description to be displayed
    max_length = 225
    # (tags are omitted by subsetting default ALLOWED_TAGS)
    #: allowed tags for bleach html stripping in description
    allowed_tags = list((set(bleach.sanitizer.ALLOWED_TAGS) - \
        set(['a', 'blockquote']))) # additional tags to remove

    class Meta:
        abstract = True

    def get_description(self):
        '''Get formatted description for preview. Uses description field
        if there is content, otherwise uses beginning of the body content.'''

        description = ''

        # use description field if set
        # use striptags to check for empty paragraph)
        if striptags(self.description):
            description = self.description

        # if not, use beginning of body content
        else:
            # Iterate over blocks and use content from first paragraph content
            for block in self.body:
                if block.block_type == 'paragraph':
                    description = block
                    # stop after the first instead of using last
                    break

        description = bleach.clean(
            str(description),
            tags=self.allowed_tags,
            strip=True
        )
        # truncate either way
        return truncatechars_html(description, self.max_length)

    def get_plaintext_description(self):
        '''Get plain-text description for use in metadata. Uses
        search_description field if set; otherwise uses the result of
        :meth:`get_description` with tags stripped.'''

        if self.search_description.strip():
            return self.search_description
        return striptags(self.get_description())


class LinkableSectionBlock(StructBlock):
    ''':class:`~wagtail.core.blocks.StructBlock` for a rich text block and an
    associated `title` that will render as an <h2>. Creates an anchor (<a>)
    so that the section can be directly linked to using a url fragment.'''
    title = CharBlock()
    anchor_text = CharBlock(help_text='Short label for anchor link')
    body = RichTextBlock(features=RICH_TEXT_TAGS)
    panels = [
        FieldPanel('title'),
        FieldPanel('slug'),
        FieldPanel('body'),
    ]

    class Meta:
        icon = 'form'
        label = 'Linkable Section'
        template = 'pages/snippets/linkable_section.html'

    def clean(self, value):
        cleaned_values = super().clean(value)
        # run slugify to ensure anchor text is a slug
        cleaned_values['anchor_text'] = slugify(cleaned_values['anchor_text'])
        return cleaned_values


class CaptionedImageBlock(StructBlock):
    ''':class:`~wagtail.core.blocks.StructBlock` for an image with
    alternative text and optional formatted caption, so
    that both caption and alternative text can be context-specific.'''
    image = ImageChooserBlock()
    alternative_text = TextBlock(required=True, help_text=ALT_TEXT_HELP)
    caption = RichTextBlock(features=['bold', 'italic', 'link'], required=False)

    class Meta:
        icon = 'image'


class BodyContentBlock(StreamBlock):
    '''Common set of blocks available in StreamFields for body text.'''
    paragraph = RichTextBlock(features=RICH_TEXT_TAGS)
    image = CaptionedImageBlock()
    linkable_section = LinkableSectionBlock()


class ContentPage(Page, PagePreviewDescriptionMixin):
    '''Basic content page model.'''

    parent_page_types = ['ContentPage']
    subpage_types = ['ContentPage']


class LandingPage(Page):
    '''Page type that aggregates and displays multiple :class:`ContentPage`s.'''

    tagline = models.CharField(max_length=255)
    body = StreamField(BodyContentBlock, blank=True)
    header_image = models.ForeignKey('wagtailimages.image', null=True,
        blank=True, on_delete=models.SET_NULL, related_name='+') # no reverse relationship

    search_fields = Page.search_fields + [index.SearchField('body')]
    content_panels = Page.content_panels + [
        FieldPanel('tagline'),
        StreamFieldPanel('body'),
        ImageChooserPanel('header_image'),
    ]

    parent_page_types = ['HomePage']
    subpage_types = ['ContentPage']


class HomePage(Page):
    '''A home page that aggregates and displays featured content.'''

    body = StreamField(BodyContentBlock, blank=True)

    class Meta:
        verbose_name = 'Homepage'

    def get_context(self, request):
        '''Add featured content to the page context.'''
        context = super().get_context(request)

        # add up to 6 featured updates, otherwise use 3 most recent updates
        updates = BlogPost.objects.featured().published().recent()[:6]
        if not updates.exists():
            updates = BlogPost.objects.published().recent()[:3]
        context['updates'] = updates

        # add up to 4 highlighted, published projects
        projects = list(Project.objects.published().highlighted())
        shuffle(projects)
        context['projects'] = projects[:4]

        # add up to 3 upcoming, published events
        context['events'] = Event.objects.published().upcoming()[:3]

        return context

    search_fields = Page.search_fields + [index.SearchField('body')]
    content_panels = Page.content_panels + [StreamFieldPanel('body')]

    parent_page_types = [Page] # only root
    subpage_types = ['LandingPage', 'ContentPage']
