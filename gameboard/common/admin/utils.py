from datetime import timedelta
import json
import pytz

from django.contrib import admin
from django.urls import reverse
from django.utils import dateformat
from django.utils.html import format_html
from django.utils.safestring import mark_safe


class BaseModelAdmin(admin.ModelAdmin):
    def truncated_id(self, instance):
        return truncated_uuid(instance.id)

    truncated_id.admin_order_field = "id"
    truncated_id.short_description = "id"

    def created_at_ist(self, instance):
        return datetime_format_ist(instance.created_at)

    created_at_ist.admin_order_field = "created_at"
    created_at_ist.short_description = "Created at IST"

    def updated_at_ist(self, instance):
        return datetime_format_ist(instance.updated_at)

    updated_at_ist.admin_order_field = "updated_at"
    updated_at_ist.short_description = "Updated at IST"

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(self.readonly_fields)
        if obj:
            fields_to_add = []
            if hasattr(obj, "created_at"):
                fields_to_add.extend(["created_at", "created_at_ist"])
            if hasattr(obj, "updated_at"):
                fields_to_add.extend(["updated_at", "updated_at_ist"])
            for field in fields_to_add:
                if field not in readonly_fields:
                    readonly_fields.append(field)
        return readonly_fields


def datetime_ist(utc_datetime_obj):
    return utc_datetime_obj.replace(tzinfo=pytz.utc).astimezone(
        pytz.timezone("Asia/Kolkata")
    )


def datetime_format(datetime_obj, output_format="N j, Y, f a"):
    df = dateformat.DateFormat(datetime_obj)
    return df.format(output_format)


def datetime_format_ist(utc_datetime_obj):
    if not utc_datetime_obj:
        return None
    ist_datetime_obj = datetime_ist(utc_datetime_obj)
    return datetime_format(ist_datetime_obj)


def formatted_duration(seconds):
    return f"{timedelta(seconds=seconds)}"


def formatted_json(json_data):
    if not json_data:
        return ""
    result = json.dumps(json_data, indent=2, sort_keys=True)
    result_str = (
        f'<pre style="margin:0;padding:0;white-space: pre-wrap;">{result}</pre>'
    )
    return mark_safe(result_str)


def formatted_json_column(json_data, max_width=None, max_height=None):
    if not json_data:
        return ""
    result = json.dumps(json_data, indent=2, sort_keys=True)
    style = "margin:0;padding:0;font-size:10px;white-space:pre-wrap;"
    if max_width is not None:
        style += f"max-width:{max_width}px;"
    if max_height is not None:
        style += f"max-height:{max_height}px;"
    result_str = f'<pre style="{style}">{result}</pre>'
    return mark_safe(result_str)


def truncated_uuid(value):
    if not value:
        return None
    truncated_value = str(value)[-12:]
    return format_html(f'<span title="{value}">{truncated_value}</span>')


def object_link(obj, display_value=None, mark_safe_for_html=True):
    if not obj:
        return None
    app_label = obj._meta.app_label
    model_label = obj._meta.model_name
    url = reverse(f"admin:{app_label}_{model_label}_change", args=(obj.id,))
    if not display_value:
        display_value = obj.id
    output = f'<a href="{url}">{display_value}</a>'
    if mark_safe_for_html:
        output = mark_safe(output)
    return output


def object_link_list(
    objects_with_display_value: list[dict], min_width=None, max_width=None
):
    """
    objects_with_display_value: [dict(object, display_value)...]
    """
    if not objects_with_display_value:
        return
    style = "padding-left: 1.2em;padding-right:0;margin:0;"
    if min_width is not None:
        style += f"min-width:{min_width}px;"
    if max_width is not None:
        style += f"max-width:{max_width}px;"
    output = f'<ul style="{style}">'
    for item in objects_with_display_value:
        obj = item["object"]
        display_value = item.get("display_value") or obj.id
        object_link_html = object_link(
            obj, display_value=display_value, mark_safe_for_html=False
        )
        output += f"<li>{object_link_html}</li>"
    output += "</ul>"
    return mark_safe(output)
