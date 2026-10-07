from django.contrib.admin import AdminSite
from django.contrib.admin.apps import AdminConfig

from .access import can_access_panel


class RoleAdminSite(AdminSite):
    def has_permission(self, request):
        return can_access_panel(request.user)


class RoleAdminConfig(AdminConfig):
    default_site = 'students.admin_site.RoleAdminSite'
