# django-related-field-display

A simple Django admin mixin to easily display and link related model fields using `__` syntax.

## Installation

```bash
pip install django-related-field-display

## Usage
Add `RelatedFieldDisplayMixin` to your admin class:
```python
from django.contrib import admin
from related_field_display import RelatedFieldDisplayMixin
from .models import YourModel

@admin.register(YourModel)
class YourModelAdmin(RelatedFieldDisplayMixin, admin.ModelAdmin):
    list_display = ('id', 'related_field__name', 'another_field')
    list_filter = ('related_field__category',)
    ordering = ('-id',)

```