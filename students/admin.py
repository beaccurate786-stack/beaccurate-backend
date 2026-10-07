from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.models import Group, User

from .admin_import import CsvImportAdminMixin
from .access import filter_students_for
from .models import Student


@admin.register(Student)
class StudentAdmin(CsvImportAdminMixin, admin.ModelAdmin):
    import_columns = ('roll_number', 'full_name', 'email', 'phone_number', 'department', 'semester', 'division', 'batch', 'status')
    import_required = ('roll_number', 'full_name', 'email', 'department', 'semester', 'division', 'batch')
    import_excluded_validation = ('student_id',)
    list_display = ('student_id', 'roll_number', 'full_name', 'department', 'semester', 'division', 'batch', 'status')
    list_filter = ('status', 'department', 'semester', 'division', 'batch')
    search_fields = ('student_id', 'roll_number', 'full_name', 'email')
    readonly_fields = ('created_at', 'updated_at')

    def get_queryset(self, request):
        return filter_students_for(request.user, super().get_queryset(request))



def _unique_email(value, exclude_pk=None):
    email = (value or '').strip()
    if not email:
        raise forms.ValidationError('Email is required.')
    users = User.objects.filter(email__iexact=email)
    if exclude_pk:
        users = users.exclude(pk=exclude_pk)
    if users.exists():
        raise forms.ValidationError('A user with this email already exists.')
    return email


class RoleUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=True,
        label='Group',
        help_text='A user belongs to exactly one group.',
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'is_staff')

    def clean_email(self):
        return _unique_email(self.cleaned_data.get('email'))

    def _save_m2m(self):
        super()._save_m2m()
        self.instance.groups.set([self.cleaned_data['role']])


class RoleUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True

    def clean_email(self):
        return _unique_email(self.cleaned_data.get('email'), exclude_pk=self.instance.pk)

    def clean_groups(self):
        groups = self.cleaned_data.get('groups')
        if groups is not None and len(groups) > 1:
            raise forms.ValidationError('A user can belong to only one group.')
        return groups


admin.site.unregister(User)


@admin.register(User)
class RoleUserAdmin(UserAdmin):
    """User admin: email is required and every user has exactly one group (role)."""

    form = RoleUserChangeForm
    add_form = RoleUserCreationForm
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'is_staff'),
        }),
    )
    filter_horizontal = ('groups', 'user_permissions')
