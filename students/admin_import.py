import csv
import io

from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import path, reverse


class CsvImportAdminMixin:
    """Adds an "Import CSV" page to a ModelAdmin.

    Subclasses set ``import_columns`` (CSV header names, all model fields) and
    ``import_required`` (the subset that must be filled in). The import is
    all-or-nothing: if any row is invalid, nothing is saved.
    """

    import_columns = ()
    import_required = ()
    import_excluded_validation = ()
    change_list_template = 'admin/csv_import_change_list.html'

    def get_urls(self):
        info = self.model._meta.app_label, self.model._meta.model_name
        custom = [
            path('import-csv/', self.admin_site.admin_view(self.import_csv_view), name='%s_%s_import_csv' % info),
            path('import-csv/sample/', self.admin_site.admin_view(self.sample_csv_view), name='%s_%s_import_sample' % info),
        ]
        return custom + super().get_urls()

    def sample_csv_view(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{self.model._meta.model_name}_import_sample.csv"'
        csv.writer(response).writerow(self.import_columns)
        return response

    def import_csv_view(self, request):
        opts = self.model._meta
        errors = []
        if request.method == 'POST' and self.has_add_permission(request):
            upload = request.FILES.get('csv_file')
            if not upload:
                errors.append('Choose a CSV file to upload.')
            else:
                created, errors = self._import(upload)
                if not errors:
                    messages.success(request, f'Imported {created} {opts.verbose_name_plural}.')
                    return redirect(reverse(f'admin:{opts.app_label}_{opts.model_name}_changelist'))

        context = {
            **self.admin_site.each_context(request),
            'opts': opts,
            'title': f'Import {opts.verbose_name_plural} from CSV',
            'columns': self.import_columns,
            'required': self.import_required,
            'errors': errors,
            'sample_url': reverse(f'admin:{opts.app_label}_{opts.model_name}_import_sample'),
            'choices': self._choice_help(),
        }
        return TemplateResponse(request, 'admin/csv_import.html', context)

    def _choice_help(self):
        help_text = {}
        for name in self.import_columns:
            field = self.model._meta.get_field(name)
            if field.choices:
                help_text[name] = ', '.join(str(value) for value, _ in field.choices)
        return help_text

    def _import(self, upload):
        try:
            text = upload.read().decode('utf-8-sig')
        except UnicodeDecodeError:
            return 0, ['File must be UTF-8 encoded CSV.']

        reader = csv.DictReader(io.StringIO(text))
        headers = [(h or '').strip().lower() for h in (reader.fieldnames or [])]
        missing = [c for c in self.import_required if c not in headers]
        if missing:
            return 0, [f'Missing required column(s): {", ".join(missing)}.']
        unknown = [h for h in headers if h not in self.import_columns]
        if unknown:
            return 0, [f'Unknown column(s): {", ".join(unknown)}.']

        errors = []
        created = 0
        try:
            with transaction.atomic():
                for line, raw in enumerate(reader, start=2):
                    row = {(k or '').strip().lower(): (v or '').strip() for k, v in raw.items()}
                    if not any(row.values()):
                        continue
                    try:
                        self._save_row(row)
                        created += 1
                    except ValidationError as exc:
                        errors.append(f'Row {line}: ' + '; '.join(exc.messages))
                if errors:
                    raise _Rollback
        except _Rollback:
            return 0, errors
        if not created:
            return 0, ['The file has no data rows.']
        return created, []

    def _save_row(self, row):
        data = {}
        for name, value in row.items():
            field = self.model._meta.get_field(name)
            if field.choices and value:
                value = self._match_choice(field, value)
            if value == '' and name not in self.import_required:
                continue
            data[name] = value
        obj = self.model(**data)
        obj.full_clean(exclude=list(self.import_excluded_validation))
        obj.save()

    @staticmethod
    def _match_choice(field, value):
        for stored, label in field.choices:
            if value.lower() in (str(stored).lower(), str(label).lower()):
                return stored
        raise ValidationError(
            f'"{value}" is not a valid {field.name}. Use one of: '
            + ', '.join(str(s) for s, _ in field.choices)
        )


class _Rollback(Exception):
    pass
