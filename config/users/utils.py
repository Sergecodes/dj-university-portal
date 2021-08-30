
def parse_phone_number(tel):
    """
    Appropriately print a phone number.
    For an odd number, separate figures before printing.
    For an even number, return same number.
    e.g. 651234566(odd number) should return 6 51 23 45 66
    """
    if len(tel) % 2 == 0:
        return tel
    
    result = tel[0]
    n = len(tel)

    for i in range(1, n, 2):
        temp = tel[i] + tel[i+1]
        result = result + ' ' + temp
    
    return result


# import uuid

# from django.contrib.auth import get_user_model
# # from django.core.cache import caches

# User = get_user_model()
# # DEFAULT_IMAGE_URL = 'imgur.co'
# DELETED_USER_EMAIL = 'deleted@gmail.com'

# # TODO this accounts should proly be created before deployment...

# def get_sentinel_user():
# 	"""
# 	A dummy profile that will be used for deleted profiles.
# 	However, deleted profiles are not purged out of the db.
# 	In case a user is deleted, set his profile to the dummy profile
# 	and set him to inactive. Don't actually delete the user!
# 	"""
# 	# store this user in cache
# 	password = str(uuid.uuid4())
# 	return User.objects.get_or_create(
# 		username='deleted',
# 		email=DELETED_USER_EMAIL,  # irrelevant dummy email
# 		defaults={'password': password, 'is_active': False}
# 	)[0]   # get_or_create() returns (obj, created?). so [0] return just the object.

