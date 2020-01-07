from django.apps import AppConfig


class PagesConfig(AppConfig):
    name = 'cdhweb.pages'
    label = 'cdhweb.pages' # will conflict with mezzanine pages otherwise
