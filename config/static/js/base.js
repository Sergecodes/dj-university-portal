'use strict';

var NAV_LINK_ACTIVE_COLOR = '#0e1e0a';
var $window = $(window);
// if you calculate the $window.width() here, you will face FOUC warnings ..
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

/** This event  */
function goToTop() {
	return;
}

/** Verify if val contains only numeric characters(digits).
 * Used in form validation.
 */
function isNumeric(val) {
	return /^\d+$/.test(val);
}

/** 
 * Called when the signup or login forms are submitted. 
 * This is to ensure that at least one phone number supports WhatsApp
 * content: what to display in the alert box
 */
function signupAndEditSubmit(e) {
	var MIN_PASSWORD_LENGTH = 8;

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
	$numberInputs.each(function(index) {
		var number = this.value;
		// remove all whitespace(space character) from number
		numbers.push(number.replace(/\s/g, ''));
	});

	phoneNumOkay = true;
	for (var i = 0; i < numbers.length; i++) {
		// if there is one invalid number
		if(!isNumeric(numbers[i])) {
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
