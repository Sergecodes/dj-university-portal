# I either give an order or my point of view. I don't give advices. - Draco
# Don't get that twisted

# export GOOGLE_APPLICATION_CREDENTIALS='/home/sergeman/Downloads/camerschools-demo-c99628e30d95.json'

** TO DO:
- on ckeditor page, when image is about to uploaded, clicking on "Browse server" opens a new window to the admin page. Prevent this.
# - create another thumbnail alias for small photos. this one will be used with small photos such that their size doesn't add. ex. in the current implementation, a photo with resolution(200 x 80) will generate a thumbnail with higher resolution and hence heavier. Use a thumbnail alias 'small_photo_thumb' and perform a size check during photo upload, perhaps from 1MB and below should use this alias, better still check the width and height of the image... (maybe sum of W and H)
- when user is logged in, reduce size of notifs and my account section on mobile.
# - validate uploaded past paper file type
- test adding image via ckeditor 
- arrange 'upload past paper button' when on mobile (see detail view.). others too like question detail ...

# freeprivacypolicy.com  (cool)
# 
# - change text in toast after bookmarking social profile 
# - in listing update and creation forms, first verify via js that contact numbers count is ok. also, if form contains errors, move page to the error section... 
# - get thumbnail of past paper pdf file. can easy_thumbnails do this... 
# - count number of downloads for past paper(download_count field) .. ajax on download button click
# - editing and creating a new item(that supports photos) pollutes the photos. (since session uses same key for updates and creations) (i don't think it's a big problem lol)
# - for watermark, if text(Camerschools.com) is too long (if image is not wide enough to contain text), insert either just Camerschools or logo..
#  - add google attribution template var(should_attribute) to context via view so as to limit reduce code, etc... 
# - enable translation for question tags, past paper comments(change model and translation.py too) and comments in qa_site
# - screen overlay or loading stuff when ajax request is called (e.g. when a thread is voted)
# highlight each occurrence of keywords in search results page.
# - add following questions on profile-qa page.. when user follows a question, the displayed toast should link to this page
# on question detail page, enable ordering answers (by date posted, votes, etc..)
# on listing pages, enable ordering (by date too..)
# - check if past paper is unique upon posting... ? if possible .
# - cached property (with ttl) package is a must ! especially for complex computations.(in future)
# - use ajax for username select ... 
# - on dashboard page, hide site points/or amount made and display only on click
# - username mentions in comments (questions)
# - validate birth date (year) in social profile; user should be above 15 ... ?. eg.ages below 15 should be rejected.. ??
# - display "some users" aside on mobile too.
# - in institution select menu, for each institution, get questions, items, adverts,past papers etc.. for that institution upon clicking.
# - student's projects app. do this one before actual launching..
# section of site where users can ask site related questions
# - after 24hrs, votes can't be recalled.
# - change the flag alert div to a toast. (create custom info toast...)
# - add repost(relist) button near posts older than x days.
# - num of characters limit control, ckeditor, comments, questions, etc..
# - don't show all comments of a post(question or answer) initially. create a button `View comments(12)` that upon clicking, will display the comments of the post. then change to hide comments..which upon clicking again hides the comments. this can surely be done using bootstrap; see example in past papers list view, levels.
# - if user is authed, on header, change profile icon to his profile image. 
# - remove duration from listings for now right... perhaps implement in future. yep.
# - you can also add the field expiry_datetime to each post (listing) then when saving, set this field to creation_datetime + ... (in short see how it's implemented in lost_or_found models.)
# - insert anchor links on each answer in question detail view so user(owner ?) can easily go to a given answer.
# - show best users on both pc and mobile; display vertically on mobile.

# - vip post(payment), birth day wish (pple with similar birthdays...); more points for answers to vip questions 
# - remove empty p tags from ck editor submitted texts.
# - try to set default for slug field in admin 
# - checkout bootstrap form validation (especially for ckeditor fields.) - .invalid-feedback, etc..
# -show loading icon during ajax request -django
# - make the element a[name='top'] have a class and attach an event to it so it should be usable  through out the site
# - create some examples (e.g. example of a good question with title body etc..) so students will have an idea of how to create theirs.
# - show help videos; e.g. how to add an image in ckedifor widget
# - add 'draft your question advice' like stackoverflow in question creation form... ?
# - add sorting by price and date  in item listing page like jumia and myschool


# - infinite scroll on mobile only in item listing page like jumia. use https://stackoverflow.com/a/45717542/10526469 pagination on mobile ?... .. bootstrap position fixed bar..
# 	. if i.is_lastnumber_in_list and i < total_num_pages;
# 		generate new pagination menu with i placed first and set i as active.
# 		followed by next items.
# 	(drop infinite scroll if too difficult or time contrained.)
# yaiero/tagify for tags.... 	stackoverflow.com/q/10839570/10526469
# - in listing detail page, print price in words on hover over.(tooltip. see num2words library)


# - test with codecov(codecoverage)
https://stackoverflow.com/questions/21941503/django-delete-unused-media-files
jquery validation plugin..

# - eventually students projects. support for ranking too


### redirect to next url.. ; use in class based views.  ###
# def get_success_url(self):
# 	try:
# 		next = self.request.GET['next']
# 	except KeyError:
# 		next = self.success_url
# 	return next


# django-anymail, django-mailer,



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
#  nb: Entities: user, Date; Relation: Activity..(num_of_votes, ...)
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


