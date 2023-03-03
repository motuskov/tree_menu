from django.db import models
from django.core.exceptions import ValidationError

from .validators import validate_path

class MenuItem(models.Model):
    '''
    Represents a menu item in databese.
    '''
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='children',
        null=True,
        blank=True,
        help_text=(
            'Parent item. Leave empty to create a top level element.'
        )
    )
    name = models.CharField(
        max_length=50,
        help_text=(
            'Menu or item name. Must be unique for a top level element.'
        )
    )
    path = models.CharField(
        max_length=100,
        validators=[
            validate_path,
        ],
        blank=True,
        help_text=(
            'Existing Django path or path name. A path has to start with "/" '
            'symbol. Can be empty for a top level element.'
        )
    )

    def __str__(self):
        return self.name

    def clean(self):
        # Checking uniqueness of menu name
        if (
            not self.parent
            and self.__class__.objects.filter(
                parent__isnull=True,
                name=self.name
            ).exists()
        ):
            raise ValidationError('Menu with the given name already exists.')

        return super().clean()
