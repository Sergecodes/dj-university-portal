'use strict';

var NAV_LINK_ACTIVE_COLOR = '#0e1e0a';
var MIN_PASSWORD_LENGTH = 8;
var MIN_LISTING_PHOTOS = 3;

var $window = $(window);
// if you calculate the $window.width() here, you might face FOUC warnings(if this script comes before body) ..
// so instead, create a global variable lastWidth and reference it later.
// var lastWidth = $window.width();
var lastWidth;
var isMobile = window.matchMedia("only screen and (max-width: 991.98px)").matches;


function headerDropdownHover() {
	var dropdownMenu = $(this).children(".dropdown-menu");
	dropdownMenu.show();

	var navLink = $(this).children("a:first-child");
	navLink.css('color', NAV_LINK_ACTIVE_COLOR);
	navLink.attr('aria-expanded', 'true');

	if(dropdownMenu.is(":visible")) {
		dropdownMenu.parent().toggleClass("show");
	}
}

function headerDropdownClick() {
	var dropdownMenu = $(this).children(".dropdown-menu");
	dropdownMenu.show();
	var navLink = $(this).children("a:first-child");
	navLink.css('color', NAV_LINK_ACTIVE_COLOR);
	navLink.attr('aria-expanded', 'true');

	// remove boostrap styles on visible dropdowns,
	// these styles are applied to the style attribute
	dropdownMenu.css({
		'position': '',
		'inset': '',
		'margin': '',
		'transform': ''
	});
}

function headerDropdownMouseLeave(event) {
	var dropdownMenu = $(this).children(".dropdown-menu");
	dropdownMenu.hide();

	var navLink = $(this).children("a:first-child");
	navLink.css('color', 'white');
	navLink.attr('aria-expanded', 'false');
}

function headerAccountInfoHoverOrClick(event) {
	var dropdownMenu = $(this).children('.dropdown-menu-end');
	dropdownMenu.addClass("show");
	dropdownMenu.show();
	dropdownMenu.css({
		'position': 'absolute',
		'inset': '0px auto auto 0px',
		'margin': '0px',
		'transform': 'translate(-96px, 67px)'
	});

	var link = $(this).children("a:first-child");
	link.attr('aria-expanded', 'true');
	link.css('filter', 'drop-shadow(rgba(255, 255, 255, 0.5) 0px 2px 5px)');
}

function headerAccountInfoMouseLeave() {
	// var dropdownMenu = $(this).children('.dropdown-menu-end');
	var dropdownMenu = $(this).children('.dropdown-menu-end');
	dropdownMenu.removeClass("show");
	dropdownMenu.hide();

	var link = $(this).children("a:first-child");
	link.attr('aria-expanded', 'false');
	link.css('filter', '');
}

function loginDropdownHoverOrClick() {
	var dropdownMenu = $(this).children('.dropdown-menu-end');
	dropdownMenu.addClass("show");
	dropdownMenu.show();
	dropdownMenu.css({
		'position': 'absolute',
		'inset': '0px auto auto 0px',
		'margin': '0px',
		'transform': 'translate(-235px, 40px)'
	});
	
}

function loginDropdownMouseLeave() {
	var dropdownMenu = $(this).children('.dropdown-menu-end');
	dropdownMenu.removeClass("show");
	dropdownMenu.hide();
}

/** 
 * Verify if val contains only numeric characters(digits). 
 * 
 * `val` string or number
 */
function isNumeric(val) {
	return /^\d+$/.test(val);
}


/** 
 * Verify if val contains only digits and spaces(and at least one digit)
 * This is the format for price and phone number
 */
function hasOnlySpacesAndDigits(val) {
	return /^(?=.*\d)[\d ]+$/.test(val);
}

/** 
 * Called when the signup or login forms are submitted. 
 * This is to ensure that at least one phone number supports WhatsApp
 * content: what to display in the alert box
 */
function signupAndEditSubmit(e) {
	// first remove previous errors from errors list 
	var $container = $('.js-errors');
	$container.text("");

	var form = e.target, data = e.data;
	var phoneNumOkay = false, passwordOkay = false, fullNameOkay = true;  // full name is true for now..

	// edit profile form has no password fields so just assume its password is okay.
	if (form.name == 'edit-profile-form') {
		passwordOkay = true;
	}

	/* Full name validation here */


	/* Password validation here  */
	// prevent validation in edit form since it doesn't contain any password field
	if (form.name != 'edit-profile-form') {
		var password = form.password.value;
		var passwordConfirm = form.confirm_password.value;
	
		// verify password length and whether password is not entirely numeric
		if (password.length < MIN_PASSWORD_LENGTH || isNumeric(password)) {
			$container.append("<p>" + data.passwordError + "</p>");
		} else {
			passwordOkay = true;
		}
	
		// note: do not set passwordOkay = true in case the passwords match. 
		// this may be wrong since the previous validation might have had errors..
		// same for other validations such as phone number..
		if (password !== passwordConfirm) {
			passwordOkay = false;
			$container.append("<p>" + data.passwordMatchError + "</p>");
		} 
	}

	/* Phone number validation here */
	// validate that numbers are valid(may contain only digits and spaces, no other characters.)
	var $numberInputs = $("tbody .numberinput");
	var numbers = [];
	// $numberInputs.each(function(index) {
	// 	var number = this.value;
	// 	// remove all whitespace(space character) from number
	// 	numbers.push(number.replace(/\s/g, ''));
	// });

	$numberInputs.each(function(index) {
		var number = this.value;
		numbers.push(number);
	})

	phoneNumOkay = true;
	for (var i = 0; i < numbers.length; i++) {
		// if there is one invalid number
		if(!hasOnlySpacesAndDigits(numbers[i])) {   // changed !isNumeric to !hasOnlySpacesAndDigits
			phoneNumOkay = false;
			$container.append("<p>" + data.phoneNumError + "</p>");
			break;
		}
	}

	// validate if numbers support WhatsApp
	var $checkboxes = $("tbody .checkboxinput");
	var can_whatsapp_list = [];
	$checkboxes.each(function() {
	  	can_whatsapp_list.push(this.checked);
  	});

	// get the number of phone numbers. this is equal to the number of checkboxes...
	var phoneNumsCount = can_whatsapp_list.length;
	for (var i = 0; i < phoneNumsCount; i++) {
		if (can_whatsapp_list[i]) {
			// at least one number supports whatsapp
			break;
		}	

		// if we're at the last phone number, (if we're here, then no number supports whatsapp.)
		if (i == phoneNumsCount-1) {
			phoneNumOkay = false;
			$container.append("<p>" + data.whatsAppError + "</p>");
		}
	}
	
	// add alert styles if there were any errors
	if (!phoneNumOkay || !passwordOkay || !fullNameOkay) {
		e.preventDefault();
		$container.addClass('alert alert-danger');
		alert(data.alertContent);

		// go to top of page so user sees errors
		var topLink = document.querySelector("a[name='top']");
		topLink.click();

		// this appends the hash character ('#') to the url, so remove this character
		// see https://stackoverflow.com/a/28155967
		window.history.replaceState({}, document.title, '.');
	}

}

/**
 * Called when the item listing form is submitted.
 */
function itemListingFormSubmit(e) {
	var form = e.target, data = e.data;
	var price = form.price.value, priceValid = false;
	var numPhotos = $('.js-gallery > .js-photo-wrp').length, photoValid = false;

	if (numPhotos >= MIN_LISTING_PHOTOS) {
		photoValid = true;
	}

	if (hasOnlySpacesAndDigits(price)) {
		priceValid = true;
	}

	if (photoValid && priceValid) {
		// do nothing, form is valid.
	} else {
		alert(data.alertContent);
	}

	// get error container and empty it just in case..
	var $photoErrWrp = $('.js-photo-errors');
	if (!photoValid) {
		e.preventDefault();
		$photoErrWrp.text('').addClass('alert alert-danger');
		$photoErrWrp.append("<p>" + data.photoError + "</p>");
	} else {
		// if photo was first invalid but is not valid..
		// in short, remove errors container just in case it is present
		$photoErrWrp.text('');
		// remove any classes such as alert, alert-danger
		$photoErrWrp.removeClass();
	}

	var $priceErrWrp = $('.js-price-errors'); 
	if (!priceValid) {
		e.preventDefault();
		$priceErrWrp.text('').addClass('alert alert-danger');
		$priceErrWrp.append("<p>" + data.priceError + "</p>");
	} else {
		$priceErrWrp.text('');
		$priceErrWrp.removeClass();
	}

}

/** 
 * Called when user selects another category in the listing category select menu
 * Also used to fill the sub category options for the default(initial) category
 */
function insertItemSubCategories(e) {
	// use this to get value instead of this.value or $(this).val() because this.value will only work when the select is changed; but we also want to call this method when the document loads.
	var categoryId = parseInt($('.js-category').first().val(), 10);

	// get the select menu containing sub category options
	var $subCategoryMenu = $('.js-subcategory');  

	$.ajax({
		url: e.data.url,
		data: {
		  'category_id': categoryId
		},
		dataType: 'json',  // data type of the result(response)
		success: function (result) {
			var subCategories = result['sub_categories'];

			// remove all options except the first
			// $('.js-subcategory > option:not(:first)').remove();
			// $subCategoryMenu.children('option').not(':first').remove();
			$subCategoryMenu.empty();
			
			$.each(subCategories, function(index, item) {
				var option = "<option value=" + item.id + ">" + item.name + "</option>";
				$subCategoryMenu.append(option);
			});
			$subCategoryMenu.prepend(" \
				<option value='' selected='selected'> \
					--------- \
				</option>"
			);
		}
	});
}


/**
 * Called when user selects another condition in the listing condition select menu
 * Also used to fill the help_text of the initial condition 
 */
function insertConditionHelpText(e) {
	// create object of type condition: help_text; get condition; create div for help text; insert help text into div.
	var $conditionMenu = $('.js-condition').first();
	var condition = $conditionMenu.val();
	var conditionsAndHelpTexts = e.data.conditions;

	var helpText = "<span class='form-text text-muted'>" + conditionsAndHelpTexts[condition] + "</span>";
	// first remove any help text that could be there
	$conditionMenu.parent().children('span:last-child').remove();
	// then insert new help text
	$conditionMenu.after(helpText);
}


/**
 * Called when user selects another item condition
 * If the item condition is new, the condition description field isn't required. otherwise, it is required.
 */
 function setDescriptionRequired(e) {
	var $conditionDescr = $('.js-condition-description');
	var condition = e.target.value;
	console.log(condition);

	if (condition === 'N') {
		$conditionDescr.removeAttr('required'); 
	} else {
		$conditionDescr.attr('required', '');
	}
}


/**
 * Called when an image of the slide is clicked
 * Displays the image in the expandable menu and places a border around the clicked image
 */
function expandImage(e) {
	// remove border from all images
	e.data.$images.css('border', 'none');

	// set border on clicked image
	var img = e.target;
	var $img = $(img);
	$img.css('border', '2px inset #198754');

	// set image as expanded image
	var $expandedImg = $('.js-expanded-img');
	$expandedImg.attr({'src': img.src, 'alt': img.alt});
}

/**
 * Display toast telling user that he needs to be logged in.
 * Toast should be present in the html page
 */
function displayLoginRequiredToast() {
	// this toast should be present in the html page !
	var $myToast = $('.js-login-required-toast').first();

	// reset styles alert-danger styles since apparently, some toast styles override them. 
	$myToast.css({
		'color': '#842029',
		'border-color': '#f5c2c7'
	});

	var bsToast = new bootstrap.Toast($myToast[0]);
	bsToast.show(); 
}

/**
 * Display toast telling user that he can't vote for his post
 * Toast should be present in the html page
 */
 function displaySelfVoteToast() {
	// this toast should be present in the html page !
	var $myToast = $('.js-self-vote-toast').first();

	// reset styles alert-danger styles since apparently, some toast styles override them. 
	$myToast.css({
		'color': '#842029',
		'border-color': '#f5c2c7'
	});

	var bsToast = new bootstrap.Toast($myToast[0]);
	bsToast.show(); 
}

/**
 * Display toast telling user that an error occurred(generally an unexpected error)
 * Toast should be present in the html page
 */
 function displayErrorOccurredToast() {
	// this toast should be present in the html page !
	var $myToast = $('.js-error-occurred-toast').first();

	// reset styles alert-danger styles since apparently, some toast styles override them. 
	$myToast.css({
		'color': '#842029',
		'border-color': '#f5c2c7'
	});

	var bsToast = new bootstrap.Toast($myToast[0]);
	bsToast.show(); 
}

/**
 * Display toast telling user that they have successfully bookmarked or unbookmarked a post
 * Toast should be present in the html page
 * `bookmarkAdded` true if bookmark was added else false
 */
 function displayListingBookmarkToggleToast(bookmarkAdded) {
	if (bookmarkAdded) 
		var $myToast = $('.js-bookmark-added-toast').first();
	else 
		var $myToast = $('.js-bookmark-removed-toast').first();

	var bsToast = new bootstrap.Toast($myToast[0]);
	bsToast.show(); 
}


/** Attach appropriate events to header dropdown menus based on media type (desktop or mobile) */
function init() {
	var $headerDropdown = $(".js-headerDropdown");
	var $headerAccountInfo = $(".js-headerAccountInfo");
	var $loginDropdown = $(".js-loginDropdown");

	isMobile = window.matchMedia("only screen and (max-width: 991.98px)").matches;
	var isDesktop = !isMobile;

	// don't enable hover on mobile screens..
	if (isDesktop) {
		$headerDropdown.hover(headerDropdownHover, headerDropdownMouseLeave);
		$headerDropdown.click(headerDropdownClick);
		$headerAccountInfo.hover(headerAccountInfoHoverOrClick, headerAccountInfoMouseLeave);
		$headerAccountInfo.click(headerAccountInfoHoverOrClick);
		$loginDropdown.hover(loginDropdownHoverOrClick, loginDropdownMouseLeave);
		$loginDropdown.click(loginDropdownHoverOrClick);

	} else if (isMobile) {
		// detach all event handlers and let Bootstrap default click functionality for dropdowns
		$headerDropdown.off();
		$headerAccountInfo.off();
		$loginDropdown.off();
	}
}

$window.on('resize', function() {
	var $this = $(this);
	var newWidth = $this.width();
	if (newWidth !== lastWidth) {
		lastWidth = newWidth;
		// console.log(lastWidth);
		init();
	}
});


$(document).ready(function() {
	init();
	lastWidth = $window.width();

	var $languageSelect = $(".js-languageSelect");
	$languageSelect.on('change', function() {
		$(this).closest('form').submit();
	});


});
