from django.core.exceptions import ValidationError
from django.urls import (
    resolve,
    reverse,
    Resolver404,
    NoReverseMatch,
)

def validate_path(value):
    '''
    Checks if path or path name exists in the project.
    '''
    # The path doesn't need, returning
    if not value:
        return
    # Checking path or path name existence
    try:
        if value.startswith('/'):
            resolve(value)
        else:
            reverse(value)
    except Resolver404:
        raise ValidationError(
            'The given path does not exist.'
        )
    except NoReverseMatch:
        raise ValidationError(
            'A path with the given name does '
            'not exist.'
        )
