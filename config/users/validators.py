from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class UsernameValidator(RegexValidator):
	"""
	Username rules:
	- Username should be between 4 to 15 characters and the first 4 characters must be letters.
	- Username should not contain any symbols, dashes or spaces.
	- All other characters are allowed(letters, numbers, hyphens and underscores).
	"""
	regex = r'\A[A-ZÀ-Ÿa-z]{4}[A-ZÀ-Ÿa-z0-9-_]{,11}\Z'
	message = _(
		'Enter a valid username. This value should be between 4 to 15 characters and the first 4 characters must be letters. It should not contain any symbols, dashes or spaces. All other characters are allowed(letters, numbers, hyphens and underscores)'
	)
	flags = 0


class FullNameValidator(RegexValidator):
	"""
	Full name rules:
	- Full name can contain only letters and hyphens.
	- It consists of two names separated by space(s).
	"""
	regex = r'\A[A-ZÀ-Ÿa-z-]+[\s]+[A-ZÀ-Ÿa-z-]+\Z'
	message = _(
		'Enter a valid full name. It should be two names separated by a space and each name may contain only letters or hyphens'
	)
	flags = 0


# def validate_full_name(full_name):
# 	""" A valid full name should be NUMBER_OF_NAMES(=2) names, e.g. Che Marcel """
# 	# number of names that full name should have
# 	NUMBER_OF_NAMES = 2  

# 	if (full_name_length := len(full_name.split())) != NUMBER_OF_NAMES:
# 		# Print different statements based on if condition
# 		if full_name_length > NUMBER_OF_NAMES:
# 			raise ValidationError(
# 				_('%(full_name)s is not valid, enter just %(number)d names'),
# 				params={'full_name': full_name, 'number': NUMBER_OF_NAMES}
# 			)
# 		else:
# 			raise ValidationError(
# 				_('%(full_name)s is not valid, enter %(number)d names'),
# 				params={'full_name': full_name, 'number': NUMBER_OF_NAMES}
# 			)



# Tel number validation has been removed
# def validate_tel_number(tel_number):
# 	""" Validate the length of the mobile number """
#	# number of digits in typical Cameroon number (e.g. 6 52 34 56 78)
# 	TEL_NUM_CHARACTERS = 9  
# 	if len(tel_number) != TEL_NUM_CHARACTERS:
# 		raise ValidationError(
# 			_("%(number)s is not a valid phone number, it doesn't have %(num_chars)d digits"),
# 			params={'number': tel_number, 'num_chars': TEL_NUM_CHARACTERS},
# 		)

# 	# if first digit is neither 6 nor 2 (for CAMTEL)
# 	if tel_number[0] != '6' and tel_number[0] != '2':
# 		raise ValidationError(
# 			_('Number must begin with either 2 or 6.')
# 		)
