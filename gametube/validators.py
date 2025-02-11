
import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class SymbolValidator:
    def validate(self, password, user=None):
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(
                _('パスワードは少なくとも1つの記号を含む必要があります。'),
                code='password_no_symbol',
            )

    def get_help_text(self):
        return _('パスワードは少なくとも1つの記号を含む必要があります。')

class UpperLowerValidator:
    def validate(self, password, user=None):
        if not re.search(r'[A-Z]', password) or not re.search(r'[a-z]', password):
            raise ValidationError(
                _('パスワードは大文字と小文字の両方を含む必要があります。'),
                code='password_no_mixed_case',
            )

    def get_help_text(self):
        return _('パスワードは大文字と小文字の両方を含む必要があります。')
