from django import forms
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.models import Group, User
from django.db import transaction
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils import timezone

from .admin_import import CsvImportAdminMixin
from .access import filter_students_for
from .enums import Batch, Division, Semester
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
    actions = ('delete_selected', 'promote_to_next_semester')

    def get_queryset(self, request):
        return filter_students_for(request.user, super().get_queryset(request))

    @admin.action(description='Promote selected students to the next semester')
    def promote_to_next_semester(self, request, queryset):
        selected = list(queryset.order_by('semester', 'division', 'roll_number'))
        if request.POST.get('confirm_promotion') == 'yes':
            invalid_assignment = any(
                request.POST.get(f'division_{student.pk}', '__keep__') not in ('__keep__', *Division.values)
                or request.POST.get(f'batch_{student.pk}', '__keep__') not in ('__keep__', *Batch.values)
                for student in selected
                if student.semester < max(Semester.values)
            )
            if invalid_assignment:
                messages.error(request, 'Choose a valid division and batch for each student before confirming.')
                return None

            promoted = 0
            skipped = 0
            with transaction.atomic():
                locked_students = {
                    student.pk: student
                    for student in Student.objects.select_for_update().filter(
                        pk__in=[student.pk for student in selected]
                    )
                }
                for preview_student in selected:
                    student = locked_students.get(preview_student.pk)
                    expected_semester = request.POST.get(f'expected_semester_{preview_student.pk}')
                    if (
                        student is None
                        or expected_semester != str(student.semester)
                        or student.semester >= max(Semester.values)
                    ):
                        skipped += 1
                        continue

                    target_division = request.POST.get(f'division_{student.pk}', '__keep__')
                    target_batch = request.POST.get(f'batch_{student.pk}', '__keep__')
                    if target_division != '__keep__':
                        student.division = target_division
                    if target_batch != '__keep__':
                        student.batch = target_batch
                    student.semester += 1
                    student.save(update_fields=('semester', 'division', 'batch', 'updated_at'))
                    promoted += 1

            if promoted:
                messages.success(request, f'Promoted {promoted} student(s) and saved their semester, division, and batch assignments.')
            if skipped:
                messages.warning(
                    request,
                    f'Skipped {skipped} student(s): they are already in the final semester or changed since the review.',
                )
            return None

        eligible = [
            (student, student.semester + 1)
            for student in selected
            if student.semester < max(Semester.values)
        ]
        final_semester = [student for student in selected if student.semester >= max(Semester.values)]
        context = {
            **self.admin_site.each_context(request),
            'title': 'Review student promotion',
            'opts': self.model._meta,
            'eligible_students': eligible,
            'final_semester_students': final_semester,
            'division_choices': Division.choices,
            'batch_choices': Batch.choices,
            'action_index': request.POST.get('index', '0'),
            'changelist_url': reverse('admin:students_student_changelist'),
        }
        return TemplateResponse(request, 'admin/students/student/promote_confirmation.html', context)



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
