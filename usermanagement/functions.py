import re
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

class CustomValidator:
    @staticmethod
    def validate_username(value):
        # Username should consist of only alphanumeric characters and underscores
        if not re.match("^[a-zA-Z0-9_]*$", value):
            raise ValidationError(
                _('Username can only contain letters, numbers, and underscores.'),
                params={'value': value},
            )

    @staticmethod
    def validate_password(value):
        # Password validation example: at least 8 characters long
        if len(value) < 8:
            raise ValidationError(
                _('Password must be at least 8 characters long.'),
                params={'value': value},
            )

    @staticmethod
    def validate_email(value):
        # Email validation example using Django's built-in EmailValidator
        validator = RegexValidator(
            regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            message=_('Enter a valid email address.'),
            code='invalid_email'
        )
        validator(value)




