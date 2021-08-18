from django.contrib.admin.helpers import checkbox
from marketplace import forms


todo:
	august 18:
		- social profile form
		- apparently, some nav dropdown links don't work when on mobile screen size. arrange this..


- screen overlay or loading stuff when ajax request is called (e.g. when a thread is voted)
- !! validate uploaded file types and sizes in views that permit file uploads !!!!!
- add datetime and poster user name after each post of question detail page; check out <a class="badge bg-info">{{}}</a>
- for all posts on site, when user posts, directly store in db and show on site. However, there should be a "flag" button that will permit them to flag the post for moderator attention.
- for desktop, in question detail page, insert ck editor directly. on mobile, user should click a button before the widget should be displayed... ?
- append (- CamerEcole) to title of each page. apparently, sites like myschool and SO do this.
- add warning text when user tries to leave page(question and listing creation forms..) window.onunload ?
- use bootstrap toasts !
- add 'draft your question advice' like stackoverflow in question creation form... ?
- add 'send_notification' field to form/model (questions creation)(exactly like myschool)..
- add possibility to enter code in ckeditor.

- for advert list page, create it as marketplace/adverts. then route both marketplace/ and marketplace/items/ to items. It should be tabs. (Items  and Adverts). clicking on one loads its page.
- add sorting by price and date  in item listing page like jumia and myschool
- infinite scroll on mobile only in item listing page like jumia. use https://stackoverflow.com/a/45717542/10526469 pagination on mobile ?... .. bootstrap position fixed bar..
	. if i.is_lastnumber_in_list and i < total_num_pages;
		generate new pagination menu with i placed first and set i as active.
		followed by next items.
	(drop infinite scroll if too difficult or time contrained.)
# yaiero/tagify for tags.... 	stackoverflow.com/q/10839570/10526469
- in listing detail page, print price in words on hover over.(tooltip. see num2words library)
- finalize listing detail page (compare with JUMIA.); also add "return to items" like myschool. add "post item" links too like both sites.
# - insert table in ckeditor widget
- insert watermark(site url) on image before saving (add logo(site url) on image before posting.)
-show loading icon during ajax request -django
- add 'FCFA' text after price input box.
- add this text before submit button (Your advert will be first reviewed by an admin before being published. Please ensure you abide by our terms, policies and the laws of the country. Myschool.com.ng reserves the right to NOT publish any item.)

- constraint on file size (maybe max 1MB)
- minimum length constraints
- when user presses button to delete photo, wait for x seconds before deleting
- remove confirm password field, implement show password checkbox

https://stackoverflow.com/questions/21941503/django-delete-unused-media-files
easy_thumbnails, pillow

TODO: users app:
- remaining front end validations (full name, )
- backend validations
- purge users db; enforce email verification on account signup (hence no captcha needed)  
(in fact, i don't think site will need captcha.) nb: use only User.objects.create_user() to create new users

- make the element a[name='top'] have a class and attach an event to it so it should be usable  through out the site

# 1. VALIDATIONS: front-end first
Full name validation:
	. no number in full name, just letters(unicode) and hyphen
	. made up of 2 strings
Password validation:
	. at least 8 chars
	. shouldn't be entirely numeric
	. passwords should match
Phone number:
	. only numbers and spaces, no other character


# photo not required for advert. 

# django-anymail, django-mailer,


# to enable getting the items that a user has bookmarked(user.bookmarked_items) and also probably the number of people that have bookmarked a user's item ?
# TODO owners won't be able to see those who bookmarked their posts, (but may see number of bookmarks?)
# means if User is deleted, set  it/bookmarker(User) to NULL

# site index view
# def index(request):
#     # get and sort items based on owner's points and creation date*
#     latest_items = ItemListing.objects.select_related('owner')\
#         .order_by('-date_added', 'owner__reputation')

#     return render(request, 'index.html', {latest_items: latest_items})


'''
previous formset code in form_valid method in UserCreateView

Now we process the phone number formset
also remove those that were marked to be deleted
phone_numbers = formset.save(commit=False)  # https://djangoproject.com/en/3.1/topics/forms/modelforms/#saving-objects-in-the-formset

for phone_number in phone_numbers:
	phone_number.owner = user
	phone_number.save()
'''

'''
def get(self, request, *args, **kwargs):
	"""
	Prevent users who aren't logged in and those whose usernames don't match with that passed in the request from editing a profile.
	"""
	user = request.user
	# if user isn't logged in, go to login page
	if not user.is_authenticated:
		return redirect(reverse('users:login'))

	# just for testing, don't forget to remove this.
	if user.username == 'sergeman':
		return super().get(request, *args, **kwargs)

	# if user is logged in but username in url isn't his, raise 404 error(like StackOverflow)
	passed_username = self.kwargs.get('username')
	if user.username != passed_username:
		raise Http404

	return super().get(request, *args, **kwargs)
'''

'''
def clean(self):
	cleaned_data = super().clean()
	password = cleaned_data.get('password')
	confirm_password = cleaned_data.get('confirm_password')

	if password != confirm_password:
		self.add_error('confirm_password', _('The passwords do not match.'))

	return cleaned_data
'''


# see https://stackoverflow.com/a/43549692
class Formset(LayoutObject):
	""" 
	Renders an entire formset, as though it were a Field.
	Accepts the names (as a string) of formset and helper as they
	are defined in the context

	Examples:
		Formset('contact_formset')
		Formset('contact_formset', 'contact_formset_helper')
	"""

	# template = "%s/formset.html" % TEMPLATE_PACK
	template = 'marketplace/formset.html'

	def __init__(self, formset_context_name, helper_context_name=None, template=None, label=None):
		self.formset_context_name = formset_context_name
		self.helper_context_name = helper_context_name

		# crispy_forms/layout.py:302 requires us to have a fields property
		self.fields = []

		# Overrides class variable with an instance level variable
		if template:
			print(template)
			self.template = template

	def render(self, form, form_style, context, **kwargs):
		formset = context.get(self.formset_context_name)
		helper = context.get(self.helper_context_name)
		# closes form prematurely if this isn't explicitly stated
		if helper:
			helper.form_tag = False

		context.update({'formset': formset, 'helper': helper})
		return render_to_string(self.template, context.flatten())


.....
@login_required
def create_item_listing(request):
	user = request.user

	if POST := request.POST:
		# Sending user object to the form so as to display user's info
		listing_form = ItemListingForm(POST, user=user)

		if listing_form.is_valid():
			new_listing = listing_form.save(commit=False)
			new_listing.owner = user
			new_listing.institution = listing_form.cleaned_data['institution']
			# new_listing.save()

			return HttpResponseRedirect('/')
		else:
			print(listing_form.errors)
	else:
		listing_form = ItemListingForm(user=user)
	
	return render(
		request, 
		'marketplace/listing_create.html', 
		{'form': listing_form}
	)


# dating
# 	- social media account (-facebook link, twitter link) for this, only users'
	- see how stackoverflow does something similar on a user's profile page
#	(usernames will be entered by user, with some help links explaining to them how to get usernames..)

# TODO reputation is not visible to users, only used internally (maybe trivial advantages, post rankings, etc..)
#  added when users confirm transaction;  also add credit points). Only a user can see his credit points

# credit points can be used for one-day-listing, {video call developer(me), site bonuses etc}



IMPLEMENTATION TIPS:
- users should not pay for each perk with cash, they should use their credit_points. However, credit points can be bought.

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

# Item categories example:
# categories: video games & consoles, toys & hobbies, sporting goods, musical instruments & gear, jewelry & watches,
# 		health & beauty,dvds & movies, crafts, dolls, computers;electronics/tablets & networking, cell phones & accessories,
# 		books,baby,produits Apple
#
# 		livres, films, jouets;instruments de musique;sport & fitness;bijoux & montres;female clothes, male clothes,
# 		female shoes,male shoes,maisons a louer,studios & chambres a louer;motos & velos;mobiles & smartphones

# Ad categories exampl:
 - job offer, event(e.g. match tomorrow..), internship, 

# this site vs jumia:
# 	- concept of points so as to encourage sellers to signal the site that the item has being bought
# 		- a certain num of points => a certain privilege e.g. be moderator?(nope..), contact developers,...
# 		- item sold => +x points to buyer and + y points to seller (x >y)
# 	- form signed upon item purchase which will serve as a receipt...  (future)
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
