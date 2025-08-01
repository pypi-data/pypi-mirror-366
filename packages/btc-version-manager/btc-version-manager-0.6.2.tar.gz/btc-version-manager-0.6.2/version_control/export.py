import csv
from typing import Collection

from django.contrib import messages
from django.db.models import QuerySet
from django.forms import BaseForm
from django.http import StreamingHttpResponse
from django.utils.decorators import method_decorator
from django.utils.html import strip_tags
from django.views.decorators.csrf import csrf_protect

from version_control.forms import RangeForm

csrf_protect_m = method_decorator(csrf_protect)


class Echo:
    """
    An object that implements just the write method of the file-like
    interface.
    """

    def write(self, value):
        """
        Write the value by returning it, instead of storing in a buffer.
        """
        return value


class ExportToCSVModelAdmin:
    """
    A class for exporting model object versions to *.csv document.
    """

    export_to_csv = True
    export_to_csv_form_class = RangeForm
    export_to_csv_filename = "csv_data_file.csv"
    export_to_csv_form_context_name = "export_to_csv_form"
    export_to_csv_error_message = "Экспорт в .csv: %s"
    export_to_csv_title = "Выгрузка в *.csv за период"
    export_to_csv_button_name = "Выгрузить"
    export_to_csv_flag = "_export_to_csv"
    export_to_csv_help_text = ""

    @csrf_protect_m
    def changelist_view(self, request, extra_context=None):
        if self.export_to_csv and self.export_to_csv_form_class:
            extra_context = extra_context or {}
            extra_context.update(
                {
                    self.export_to_csv_form_context_name: self.export_to_csv_form_class(),
                    "export_to_csv": self.export_to_csv,
                    "export_to_csv_title": self.export_to_csv_title,
                    "export_to_csv_button_name": self.export_to_csv_button_name,
                    "export_to_csv_flag": self.export_to_csv_flag,
                    "export_to_csv_help_text": self.export_to_csv_help_text,
                }
            )

            # *.csv export
            if self.export_to_csv and self.export_to_csv_flag in request.POST:
                response = self.handle_csv_export(request, extra_context)
                if response:
                    return response

        return super().changelist_view(request, extra_context=extra_context)

    def handle_csv_export(self, request, context):
        form = self.export_to_csv_form_class(data=request.POST)
        if form.is_valid():
            queryset = self.get_csv_data_queryset(form=form)
            rows = self.get_csv_data_rows(queryset) or []
            pseudo_buffer = Echo()
            writer = csv.writer(pseudo_buffer)
            response = StreamingHttpResponse((writer.writerow(row) for row in rows), content_type="text/csv")
            response["Content-Disposition"] = f'attachment; filename="{self.export_to_csv_filename}"'
            return response
        else:
            errors = ", ".join(set([strip_tags(error) for error in form.errors.values()]))
            messages.warning(request, self.export_to_csv_error_message % errors.lower())
            context.update({self.export_to_csv_form_context_name: form})

    def get_csv_data_rows(self, queryset: QuerySet) -> Collection:
        pass

    def get_csv_data_queryset(self, form: BaseForm) -> QuerySet:
        return self.model.objects.none()
