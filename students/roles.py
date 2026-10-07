from django.contrib.auth.management import create_permissions
from django.contrib.auth.models import Group, Permission

from .enums import Role

# Models a HOD must not touch: group creation and raw permission rows.
HOD_EXCLUDED_MODELS = {('auth', 'group'), ('auth', 'permission')}


def sync_role_groups(sender, using='default', apps=None, **kwargs):
    """Create the role groups after migrate. Existing groups keep any edits."""
    from django.apps import apps as global_apps

    for app_config in global_apps.get_app_configs():
        create_permissions(app_config, verbosity=0, using=using)

    everything = Permission.objects.using(using).select_related('content_type')

    # Super Admin always holds every permission, including ones from newly added apps.
    super_admin, _ = Group.objects.using(using).get_or_create(name=Role.SUPER_ADMIN)
    super_admin.permissions.set(everything)

    # HOD gets new permissions as apps are added; anything removed by hand stays removed.
    hod, created = Group.objects.using(using).get_or_create(name=Role.HOD)
    allowed = [
        p for p in everything
        if (p.content_type.app_label, p.content_type.model) not in HOD_EXCLUDED_MODELS
    ]
    if created:
        hod.permissions.set(allowed)
    else:
        known = set(hod.permissions.values_list('pk', flat=True))
        hod.permissions.add(*[p for p in allowed if p.content_type.app_label == 'timetable' and p.pk not in known])

    mentor, created = Group.objects.using(using).get_or_create(name=Role.MENTOR)
    if created:
        mentor.permissions.set(
            everything.filter(content_type__app_label='students', content_type__model='student', codename='view_student')
        )

    # Students are data only: the group carries no permissions and no panel access.
    Group.objects.using(using).get_or_create(name=Role.STUDENT)
