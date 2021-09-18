# I either give an order or my point of view. I don't give advices. - Draco
# Don't get that twisted
# camerschools ?? - yep

# geeksforgeeks.org/built-in-custom-model-managers-in-django	

todo:
		Sep 13
			# - implement permissions (moderator) (PermissionsMixin...)
			- update user profile/dashboard accordingly
			- social_profile_detail.html page. upon clicking on the name of a user, go to this page.
			- insert delete and edit links. ps moderator can delete only if post has x num of flags.
		
		- notifications(small practices on django-notifications-hq perhaps via terminal)

		- questions following ( icons...) both academic question / school-based.
		- username @username ... mentions 
		- share links on detail pages... 
		- test item listing list filter

		### update(edit views) ### (do those other sites permit this ?)
		- questions/answers/comments (remember restrictions on edits and deletions; num_of likes, etc..). hide delete button to ensure restriction. ensure too that update and delete views enforce restrictions.

- remove poster from list view ??
- apply style to current nav link.
- so-so signal sent after a flag, to update some fields etc..
- add restriction for downvote(num of likes required) in frontend and backend
- don't show all comments of a post(question or answer) initially. create a button `View comments(12)` that upon clicking, will display the comments of the post. then change to hide comments..which upon clicking again hides the comments. this can surely be done using bootstrap; see example in past papers list view, levels.
- in the search forms, does searching for 'mercedes benz' give results containing only mercedes or benz respectively ? this should definitely be the case ! ensure this.
- use dropdown-menu-end on soclialize link like user=account.(generally, arrange the header.) it should be responsive
- for any textarea that can't be resized (horizontally), try removing the width on the font-control class.. eg. ckeditor
- try to set self.object in mixin; (self.object=self.object()) to prevent calling it again in post.
- change owner to poster.. marketplace.
- create a general usage page where each section of the site will be explained. eg. Questions:
you can't see the user that likes ur posts...
- change question voting to json response ..
- implement editing and deleting by poster in various apps..	
- if user is authed, on header, change profile icon to his profile image. 
- arrange socialize dropdown...
- remove all exceptions raised in server-side, apart from in forms. (assert and raise)
- remove duration from listings for now right... perhaps implement in future. yep.
- you can also add the field expiry_datetime to each post (listing) then when saving, set this field to creation_datetime + ... (in short see how it's implemented in lost_and_found models.)
- convert all lists with div to ul > li; 
- add page to questions/ like my school; same with marketplace/ ; explaining difference between items and adverts...
- remove zip filter from template and do the zip in view. ?... django performance improvement recommendations
- remove default_language hidden field from template and assign it in view...
- add select_related... on filter views. (overriden qs property)
- clicking on a university in a listing should filter results by that university.  = show optional text if no item is on listing page...
- make ckeditor field colored after form invalid. eg. set border: 1px solid red on the django-ckeditor-widget and its following span.invalid-feedback to d-block
- convert index page each section to the other myschool format... (see screenshot in phone)
# profile/qa site
- insert anchor links on each answer in question detail view so user(owner ?) can easily go to a given answer.
- add my answers(aca and school-based) and my bookmarked questions.
- abeg use prefetch_related and select_related in situations of duplicate queries ! !!!
see example in profile/QA view.. there should be no duplicate queries on any page !!!
- change pencil icon to may be microphone icon in question detail.
- remove unneccessary margin and padding classes and use responsive ones such as me-sm-0, my-sm-2, etc...
- in item/ad listing, make tab items clickable (links.)
- show best users on both pc and mobile; display vertically on mobile.
- tell user his age won't be visible to other users.
- label pages sections for accessibility...
- reduce size (height) of listing results.
- initially, remove count of items. perhaps in future, will display count...
- remove unused css class name from each template. use comments for potential future class names .
- tell users during account creation that their phone numbers and other private stuff... won't be visible to other users . ; perhaps via help_text under the phone_numbers field.
- remove tags from school questions ...?
- in create forms, convert 'raise' to sef.add_error()
- before(above) each create view, create a sort of bootstrap alert that explains users the use ...; also say that all fields marked or ending with * are required.
- in list views, use thumbnails of images. can append thumbnail image with '_thumb'...
- add email to contact details in detail views.
- when filtering, consider only 'unexpired' posts. (`is_outdated` field on all 'outdate-able' models.); also add an index on this field.
- change all datetime_added fields to posted_datetime (for most models where it makes sense;). all models hould have this field. (datetime_added for moderator only models and posted_datetime for users.)
- backgound-color on filter forms(see ex form marketplace )
- optimize queries, especially on list view. selec_related on poster...
- photo upload modal stuff too for past_papers site
- enforce MIN_LISTING_PHOTOS_LENGTH for item listing creation. return form_invalid... ? 
- number of results when filtering.. ?
- vip post(payment), birth day wish (pple with similar birthdays...); more points for answers to vip questions 
- remove tags (SchoolQuestionTag) from SchoolQuestion model (i dont think its necessary). perhaps in future we'll need to add tags to questions (like stack overflow). in fact, tags to listings too using django-taggit
- when listing forms have errors, ensure previously uploaded photos are maintained ! 
- remove empty p tags from ck editor submitted texts.
- one page for posts deletion.
- place common models in core app such as Institution, PhoneNumber, 
- add original_language field for most models ... Yep !! remove it from frontend. it should be set on backend since user could easily modify its value on the frontend.
- change external_link_svg to font-awesome icon
- add asterisk after condition_description when condition changes. (to show the description is required)
- permissions.
- footer. check out font awesome's footer on mobile., ilost.co's footer too
- try to set default for slug field in admin 
- checkout bootstrap form validation (especially for ckeditor fields.) - .invalid-feedback, etc..
- insert watermark(site url) on image before saving (add logo(site url) on image before posting.)
-show loading icon during ajax request -django
- enable bookmarking of posts. (questions, listings)
- add 'FCFA' text after price input box.
- add this text before submit button (Your advert will be first reviewed by an admin before being published. Please ensure you abide by our terms, policies and the laws of the country. Myschool.com.ng reserves the right to NOT publish any item.)
- listings should disappear(be deleted or hidden) after duration expires
- create next links to redirect to needed templates after user leaves that page. e.g redirect back to listing create view when user clicks on edit profile number and finishes editing
- include means to refer to another user then commenting in qa_site app. eg. @sergeman you could better explain that. then sergeman should be notified... ?
- create some examples (e.g. example of a good question with title body etc..) so students will have an idea of how to create theirs.
- limit number of images in past paper upload...
- all create forms should have shadows. and other forms normal borders
- socialize detail form should take visitor to socialize section of user's profile
- limit number of answers per question and comments per post in qa_site app.
- style ckeditor widgets, height, add possibility to enter code, maths, where required !; add placeholder in ckeditor comment forms... i don't think placeholders will be possible. if not possible, add help text below 'Add a comment' button with desired content of placeholder; (see stackoverflow comment placeholder) 
- set max-height of all ckeditor images (images posted via ckeditor  to say 200px;
- screen overlay or loading stuff when ajax request is called (e.g. when a thread is voted)
- !! validate uploaded file types and sizes in views that permit file uploads !!!!!
- add datetime and poster user name after each post of question detail page; check out <a class="badge bg-info">{{}}</a>
- use ajax for username select ... 
- send notification to user when he creates a form
- translations !
- correct phone number input in user forms. try adding a prefix on the formset.
-also, apparently, password similarity check isn't properly working. test this too. also test on shell.  add full name similarity check.
- for all posts on site, when user posts, directly store in db and show on site. However, there should be a "flag" button that will permit them to flag the post for moderator attention.
- for desktop, in question detail page, insert ck editor directly. on mobile, user should click a button before the widget should be displayed... ?
- append (- CamerEcole) to title of each page. apparently, sites like myschool and SO do this.
- add warning text when user tries to leave page(question and listing creation forms..) window.onunload ?
- show help videos; e.g. how to add an image in ckedifor widget
- add 'draft your question advice' like stackoverflow in question creation form... ?
- add 'send_notification' field to form/model (questions creation)(exactly like myschool)..
- messages framework django..
- add sorting by price and date  in item listing page like jumia and myschool
- infinite scroll on mobile only in item listing page like jumia. use https://stackoverflow.com/a/45717542/10526469 pagination on mobile ?... .. bootstrap position fixed bar..
	. if i.is_lastnumber_in_list and i < total_num_pages;
		generate new pagination menu with i placed first and set i as active.
		followed by next items.
	(drop infinite scroll if too difficult or time contrained.)
# yaiero/tagify for tags.... 	stackoverflow.com/q/10839570/10526469
- in listing detail page, print price in words on hover over.(tooltip. see num2words library)
- finalize listing detail page (compare with JUMIA.); also add "return to items" like myschool. add "post item" links too like both sites.

- constraint on file size (maybe max 1MB)
- minimum length constraints
- remove confirm password field, implement show password checkbox

- test with codecov(codecoverage)
https://stackoverflow.com/questions/21941503/django-delete-unused-media-files
easy_thumbnails, pillow
jquery validation plugin..

- eventually students projects. support for ranking too

TODO: users app:
- remaining front end validations (full name, )
- backend validations
- purge users db; enforce email verification on account signup (hence no captcha needed)  
(in fact, i don't think site will need captcha.) nb: use only User.objects.create_user() to create new users

- make the element a[name='top'] have a class and attach an event to it so it should be usable  through out the site


### redirect to next url.. ; use in class based views.  ###
def get_success_url(self):
	try:
		next = self.request.GET['next']
	except KeyError:
		next = self.success_url
	return next

### to get users tags from question creation form,  ###
user enters 'tag1, tag2,   tag3'
tags = self.cleaned_data.get('tags')
correct_tags = ''
# validate: remove all other characters apart from comma.
# in frontend, tell user that tags will be correctly parsed. 
for char in tags:
	if char is alphanumeric or char is comma or char is space:
		correct_tags += char

tags_list = tags.replace(' ', '').split(',')
# returns tags_list = ['tag1', 'tag2', 'tag3']

# django-anymail, django-mailer,


# to enable getting the items that a user has bookmarked(user.bookmarked_items) and also probably the number of people that have bookmarked a user's item ?
# TODO owners won't be able to see those who bookmarked their posts, (but may see number of bookmarks?)
# means if User is deleted, set  it/bookmarker(User) to NULL


- cached property (with ttl) package is a must ! especially for complex computations.(in future)



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
