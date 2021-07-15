from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

TEL_NUM_CHARACTERS = 9  # number of digits in typical Cameroon number (e.g. 6 52 34 56 78)
NUMBER_OF_NAMES = 2  # number of names that full name should have


def validate_tel_number_length(tel_number):
	""" Validate the length of the mobile number """
	if len(tel_number) != TEL_NUM_CHARACTERS:
		raise ValidationError(
			_("%(number)d is not a valid phone number, it doesn't have %(num_chars)d digits"),
			params={'number': tel_number, 'num_chars': TEL_NUM_CHARACTERS},
		)
	elif tel_number[0] != '6' or tel_number[0] != '2':  # first character should be 6 or 2(CAMTEL)
		raise ValidationError(
			_('Number must begin with either 2 or 6.')
		)


def validate_full_name(full_name):
	""" A valid full name should be NUMBER_OF_NAMES(=2) names, e.g. Che Marcel """
	if (full_name_length := len(full_name.split())) != NUMBER_OF_NAMES:
		# Print different statements based on if condition
		if full_name_length > NUMBER_OF_NAMES:
			raise ValidationError(
				_('%(full_name)s is not valid, enter just %(number)d names'),
				params={'full_name': full_name, 'number': NUMBER_OF_NAMES}
			)
		else:
			raise ValidationError(
				_('%(full_name)s is not valid, enter %(number)d names'),
				params={'full_name': full_name, 'number': NUMBER_OF_NAMES}
			)
