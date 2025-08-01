# django-related-field-display

A simple Django admin mixin to easily display and link related model fields using `__` syntax.

This package allows you to use the double underscore (`__`) syntax in `list_display` and `list_filter` attributes of Django admin classes to display related model fields without needing to write custom methods or properties.

This project is inspired from [django-admin-related](https://github.com/PetrDlouhy/django-related-admin) package, but it is deprecated and not maintained anymore.

## Installation

```bash
pip install django-related-field-display
```

## Usage
```python
from django.contrib import admin
from related_field_display.admin import RelatedFieldDisplayMixin
from .models import YourModel

@admin.register(YourModel)
class YourModelAdmin(RelatedFieldDisplayMixin, admin.ModelAdmin):
    list_display = ('id', 'related_field__name', 'another_field')
    list_filter = ('related_field__category',)
    ordering = ('-id',)
```

## PyPI
[![PyPI version](https://badge.fury.io/py/django-related-field-display.svg)](https://pypi.org/project/django-related-field-display/)