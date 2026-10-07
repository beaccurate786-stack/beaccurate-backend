from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from students.enums import Role

from .models import Faculty


def ensure_faculty_profile(user):
    """Create a Faculty profile for a mentor user. HOD completes department/semester/division."""
    if hasattr(user, 'faculty_profile'):
        return
    email = user.email or f'{user.username}@pending.invalid'
    if Faculty.objects.filter(email=email).exists():
        return
    Faculty.objects.create(
        user=user,
        full_name=user.get_full_name() or user.username,
        email=email,
        phone_number='',
        department='',
        division='',
    )


@receiver(m2m_changed, sender=get_user_model().groups.through, dispatch_uid='faculty_profile_for_mentor')
def create_profile_for_mentor(sender, instance, action, reverse, pk_set, **kwargs):
    if action != 'post_add':
        return
    User = get_user_model()
    if reverse:  # group.user_set.add(...) -> instance is the Group
        if instance.name != Role.MENTOR:
            return
        users = User.objects.filter(pk__in=pk_set)
    else:  # user.groups.add(...) -> instance is the User
        if not instance.groups.filter(pk__in=pk_set, name=Role.MENTOR).exists():
            return
        users = [instance]
    for user in users:
        ensure_faculty_profile(user)


@receiver(m2m_changed, sender=get_user_model().groups.through, dispatch_uid='single_group_per_user')
def enforce_single_group(sender, instance, action, reverse, pk_set, **kwargs):
    """A user belongs to one group only, however the groups are assigned."""
    if action != 'pre_add':
        return
    User = get_user_model()
    if reverse:  # instance is a Group
        for user in User.objects.filter(pk__in=pk_set):
            if user.groups.exclude(pk=instance.pk).exists():
                raise ValidationError(f'{user} already belongs to a group; a user can have only one.')
    elif instance.groups.exclude(pk__in=pk_set).exists() or len(pk_set) > 1:
        raise ValidationError(f'{instance} can belong to only one group.')
