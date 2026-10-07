from django.db.models import Q

from .enums import Role


def is_mentor_only(user):
    """A mentor who has no broader role: sees only the students of their faculty class."""
    if not user.is_authenticated or user.is_superuser:
        return False
    roles = set(user.groups.values_list('name', flat=True))
    return Role.MENTOR in roles and not roles & {Role.SUPER_ADMIN, Role.HOD}


def filter_students_for(user, queryset):
    """Mentors see students whose semester and division match their faculty profile."""
    if not is_mentor_only(user):
        return queryset
    faculty = getattr(user, 'faculty_profile', None)
    if faculty is None or faculty.semester is None or not faculty.division:
        return queryset.none()
    return queryset.filter(Q(semester=faculty.semester, division=faculty.division))


def can_access_panel(user):
    """Staff users may enter the admin, except accounts that only hold the Student role."""
    if not (user.is_active and user.is_staff):
        return False
    if user.is_superuser:
        return True
    roles = set(user.groups.values_list('name', flat=True))
    return not (Role.STUDENT in roles and not roles - {Role.STUDENT})
