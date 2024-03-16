from collections import deque
from django.core.exceptions import ValidationError
from django.db import models
import json


class DequeField(models.Field):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        return name, path, args, kwargs
    
    
    
    def from_db_value(self, value, expression, connection):
        if value is None:
            return None
        return deque(json.loads(value)) 

    def to_python(self, value):
        if value is None:
            return None  # If the value is None, return None
        if not isinstance(value, deque):
            raise ValidationError("Value must be a deque instance.")
        return value  # Otherwise, return the value as is

    def get_prep_value(self, value):
        if isinstance(value, deque):
            # Serialize deque into a JSON string for storage
            return json.dumps(list(value))
        return value

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        return self.get_prep_value(value)




