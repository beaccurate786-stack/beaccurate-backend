from django.apps import AppConfig
from django.db.models.signals import post_migrate


class StudentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'students'

    def ready(self):
        from .roles import sync_role_groups

        post_migrate.connect(sync_role_groups, sender=self, dispatch_uid='students_sync_role_groups')

