from django.urls import reverse
from django.utils.html import format_html

class RelatedFieldDisplayMixin:
    def __getattr__(self, name):
        if "__" in name:
            parts = name.split("__")
            if len(parts) == 2:
                field_name, related_field = parts

                def method(obj):

                    related_obj = getattr(obj, field_name, None)
                    if not related_obj:
                        return "-"

                    field_value = getattr(related_obj, related_field, "-")
                    if field_value in ("-", None, ""):
                        return "-"

                    app_label = related_obj._meta.app_label
                    model_name = related_obj._meta.model_name
                    try:
                        admin_url = reverse(
                            f'admin:{app_label}_{model_name}_change',
                            args=[related_obj.pk]
                        )
                        return format_html('<a href="{}" target="_blank">{}</a>', admin_url, field_value)
                    except:
                        return field_value

                method.short_description = f"{field_name.replace('_', ' ').title()} {related_field.title()}"
                method.admin_order_field = f"{field_name}__{related_field}"
                method.allow_tags = True

                setattr(self, name, method)
                return method

        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")