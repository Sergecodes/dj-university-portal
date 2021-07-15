# no null=True needed for char and text fields. default for blank & null is False.
# if no value is set and the field is nullable, the value is stored in the database as an empty string ('')


# dating
# 	- social media account (-facebook link, twitter link) for this, only users'
#	(usernames will be entered by user, with some help links explaining to them how to get usernames..)

# TODO reputation is not visible to users, only used internally (maybe trivial advantages, post rankings, etc..)
#  added when users confirm transaction;  also add credit points). Only a user can see his credit points

# credit points can be used for one-day-listing, {video call developer(me), site bonuses etc}



IMPLEMENTATION TIPS:
- users should not pay for each perk with cash, they should use their credit_points. However, credit points can be bought.
- during registration, ask all users info, with a text telling them where the particuar info will be used. eg. Enter your phone number: -This will be used only in the marketplace section-

# TODO moderator should have his own view of the site; they should be able to see pending reports, etc.
# TIPS:
# scheduling listing
# on items page, give user tip that "if he sees an item he's interested in, he should contact the
# owner if the price if understandable. They may still bargain on an agreeable price"

# make money when user post ads:
# bold title in search results (like ebay) cheapest
# subtitle in listing
# boost up posts(faire remonter) (like jumia) cheaper
# vip (like jumia)

# on post description, user shouldnt put contact details nor now web links (scam, spam, etc..)
# In fact, remove all weblinks from source b4 adding to db..

#
# categories: video games & consoles, toys & hobbies, sporting goods, musical instruments & gear, jewelry & watches,
# 		health & beauty,dvds & movies, crafts, dolls, computers;electronics/tablets & networking, cell phones & accessories,
# 		books,baby,produits Apple
#
# 		livres, films, jouets;instruments de musique;sport & fitness;bijoux & montres;female clothes, male clothes,
# 		female shoes,male shoes,maisons a louer,studios & chambres a louer;motos & velos;mobiles & smartphones

# this site vs jumia:
# 	- concept of points so as to encourage sellers to signal the site that the item has being bought
# 		- a certain num of points => a certain privilege e.g. be moderator?(nope..), contact developers,...
# 		- item sold => +x points to buyer and + y points to seller (x >y)
# 	- form signed upon item purchase which will serve as a receipt...
# 	- users can only perform transaction in  items in univ, hence more security...



# how do you do this in db: "you have 10 votes left for today? "
# TODO nb: Entities: user, Date; Relation: Activity..(num_of_votes, ...)
'''
class User:
	activity_dates = models.ManyToManyField(
		'ActivityDate',
		through='UserActivity',
		related_name='+'  # disable mapping reverse relation (from ActivityDate to User).
		# so no way to do activity_date.user etc.  no need to do this right
	)

	def add_vote(self):
		...
		self.dates.latest
	...

class ActivityDate(models.Model):
	datetime = models.DateTimeField(auto_now_add=True)

class UserActivity(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	activity_date = models.ForeignKey(Date, on_delete=models.CASCADE)

	# Relation fields:
	num_of_votes_left = models.PositiveIntegerField(default=10)


	class Meta:
		# order_with_respect_to = 'activity_date'
		unique_together = [
			('user', 'activity_date'),
		]
	# then a cron job to remove all entries with date < current date
	# from django.utils.timezone import localtime, now
	remove all entries where entry.datetime.date() < timezone.now().date
'''

# Sentinel user/profile stuff (if user has to be really deleted from db)

# DELETED_USER_EMAIL = 'deleted@gmail.com'
# def get_sentinel_profile():
# 	"""
# 	A dummy profile that will be used for deleted profiles.
# 	However, deleted profiles are not purged out of the db.
# 	:return: sentinel profile
# 	"""
# 	# store this profile in cache.
# 	password = str(uuid.uuid4())  # at least the password should not be guessable!
# 	sentinel_user = User.objects.get_or_create(
# 		username='deleted',
# 		email=DELETED_USER_EMAIL,  # fraudulent irrelevant email
# 		defaults={'password': password, 'is_active': False}
# 	)[0]  # get_or_create() returns (obj, created?). so [0] return just the object.
#
# 	return sentinel_user.profile  # remember, when a user is created, a profile is also created for him
# def get_sentinel_user():
# 	"""
# 	In case a user is deleted, set his profile to the dummy profile
# 	and set him to inactive. Don't actually delete the user!
# 	"""
# 	# store this user in cache
# 	password = str(uuid.uuid4())
# 	return User.objects.get_or_create(
# 		username='deleted',
# 		email=DELETED_USER_EMAIL,  # fraudulent irrelevant email
# 		defaults={'password': password, 'is_active': False}
# 	)[0]
