from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

from core.constants import INVALID_TAG_CHARS


class UsernameValidator(RegexValidator):
	"""
	Username rules:
	- Username should be between 4 to 15 characters and the first 4 characters must be all letters.
	- Username should not contain any symbols, dashes or spaces.
	- All other characters are allowed(letters, numbers, hyphens and underscores).
	"""
	regex = r'\A[A-ZÀ-Ÿa-z]{4}[A-ZÀ-Ÿa-z0-9-_]{0,11}\Z'
	message = _(
		'Enter a valid username. This value should be between 4 to 15 characters and the first 4 characters must be all letters. \n '
		'It should not contain any symbols, dashes or spaces. All other characters are allowed(letters, numbers, hyphens and underscores)'
	)
	flags = 0


def validate_question_tags(tags: list, max_length):
	n = len(tags)
	if n > max_length:
		raise ValidationError(
			_('Enter at most %(max_tags)d tags; you entered %(number)d.'),
			params={'max_tags': max_length, 'number': n}
		)

	tag_str = ''.join(tags)
	if any(char in INVALID_TAG_CHARS for char in tag_str):
		raise ValidationError(_('Only alphanumeric characters and hyphens are permitted'))

