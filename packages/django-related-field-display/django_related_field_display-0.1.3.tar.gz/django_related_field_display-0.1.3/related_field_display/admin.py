from django.urls import reverse
from django.utils.html import format_html

class RelatedFieldDisplayMixin:
    def __getattr__(self, name):
        if "__" in name:
            parts = name.split("__")
            if len(parts) >= 2:  # Changed from == 2 to >= 2 to support multiple relations
                relation_path = parts[:-1]  # All parts except the last one (field name)
                field_name = parts[-1]      # Last part is the field name

                def method(obj):
                    # Traverse through the relation chain
                    current_obj = obj
                    final_related_obj = None
                    
                    # Follow the relation path
                    for relation in relation_path:
                        current_obj = getattr(current_obj, relation, None)
                        if not current_obj:
                            return "-"
                        final_related_obj = current_obj
                    
                    # Get the final field value
                    field_value = getattr(final_related_obj, field_name, "-")
                    if field_value in ("-", None, ""):
                        return "-"

                    # Generate admin URL for the final related object
                    app_label = final_related_obj._meta.app_label
                    model_name = final_related_obj._meta.model_name
                    try:
                        admin_url = reverse(
                            f'admin:{app_label}_{model_name}_change',
                            args=[final_related_obj.pk]
                        )
                        return format_html('<a href="{}" target="_blank">{}</a>', admin_url, field_value)
                    except:
                        return field_value

                # Create a more descriptive title from the full relation path
                relation_title = " ".join([part.replace('_', ' ').title() for part in relation_path])
                field_title = field_name.replace('_', ' ').title()
                method.short_description = f"{relation_title} {field_title}"
                method.admin_order_field = name  # Use the full name for ordering
                method.allow_tags = True

                setattr(self, name, method)
                return method

        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")