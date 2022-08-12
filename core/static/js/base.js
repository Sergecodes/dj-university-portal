'use strict';

var NAV_LINK_ACTIVE_COLOR = '#0e1e0a';
var CURRENT_NAV_LINK_CLASS = 'nav-menu__link--current';
var MIN_PASSWORD_LENGTH = 8;
var MIN_LISTING_PHOTOS = 3;

var $window = $(window);
// if you calculate the $window.width() here, 
// you might face FOUC warnings(if this script comes before body) ..
// so instead, create a global variable lastWidth and reference it later.
// var lastWidth = $window.width();
var lastWidth;
var isMobile = window.matchMedia("only screen and (max-width: 991.98px)").matches;


function headerDropdownHover(e) {
	var $this = $(this);
	var dropdownMenu = $this.children(".dropdown-menu");
	dropdownMenu.show();

	var $navLink = $this.children("a:first-child");

	// if nav link isn't for current page, set color...
	if (!$navLink.hasClass(CURRENT_NAV_LINK_CLASS)) {
		$navLink.css('color', NAV_LINK_ACTIVE_COLOR);
	}
	$navLink.attr('aria-expanded', 'true');

	if (dropdownMenu.is(":visible")) {
		dropdownMenu.parent().toggleClass("show");
	}
}

function headerDropdownClick(e) {
	var $this = $(this);
	var dropdownMenu = $this.children(".dropdown-menu");
	dropdownMenu.show();
	var $navLink = $this.children("a:first-child");

	// if nav link isn't for current page, set color...
	if (!$navLink.hasClass(CURRENT_NAV_LINK_CLASS)) {
		$navLink.css('color', NAV_LINK_ACTIVE_COLOR);
	}
	$navLink.attr('aria-expanded', 'true');

	// remove boostrap styles on visible dropdowns,
	// these styles are applied to the style attribute
	dropdownMenu.css({
		'position': '',
		'inset': '',
		'margin': '',
		'transform': ''
	});
}

function headerDropdownMouseLeave(e) {
	var $this = $(this);
	var dropdownMenu = $this.children(".dropdown-menu");
	dropdownMenu.hide();

	var $navLink = $this.children("a:first-child");

	// if nav link isn't for current page, set color to white(default)
	if (!$navLink.hasClass(CURRENT_NAV_LINK_CLASS)) {
		$navLink.css('color', 'white');
	}
	$navLink.attr('aria-expanded', 'false');
}

function headerAccountInfoHoverOrClick(e) {
	var $this = $(this);
	var dropdownMenu = $this.children('.dropdown-menu-end');
	dropdownMenu.addClass("show");
	dropdownMenu.show();
	dropdownMenu.css({
		'position': 'absolute',
		'inset': '0px auto auto 0px',
		'margin': '0px',
		'transform': 'translate(-96px, 67px)'
	});

	var link = $this.children("a:first-child");
	link.attr('aria-expanded', 'true');
	link.css('filter', 'drop-shadow(rgba(255, 255, 255, 0.5) 0px 2px 5px)');
}

function headerAccountInfoMouseLeave(e) {
	var $this = $(this);
	var dropdownMenu = $this.children('.dropdown-menu-end');
	dropdownMenu.removeClass("show");
	dropdownMenu.hide();

	var link = $this.children("a:first-child");
	link.attr('aria-expanded', 'false');
	link.css('filter', '');
}

function loginDropdownHoverOrClick(e) {
	var $this = $(this);
	var dropdownMenu = $this.children('.dropdown-menu-end');
	dropdownMenu.addClass("show");
	dropdownMenu.show();
	dropdownMenu.css({
		'position': 'absolute',
		'inset': '0px auto auto 0px',
		'margin': '0px',
		'transform': 'translate(-235px, 40px)'
	});
}

function headerLangDropdownHover(e) {
	var $this = $(this);
	var dropdownMenu = $this.find('.dropdown-menu');
	dropdownMenu.addClass("show");
	dropdownMenu.show();

	$this.find('.dropdown-toggle').attr('aria-expanded', 'true');
}

function headerLangDropdownMouseLeave(e) {
	var $this = $(this);
	var dropdownMenu = $this.find('.dropdown-menu');
	dropdownMenu.removeClass("show");
	dropdownMenu.hide();
	$this.find('.dropdown-toggle').attr('aria-expanded', 'false');
}

function loginDropdownMouseLeave(e) {
	var dropdownMenu = $(this).children('.dropdown-menu-end');
	dropdownMenu.removeClass("show");
	dropdownMenu.hide();
}

/** 
 * Verify if val contains only numeric characters(digits). 
 * `val` string or number
 */
function isNumeric(val) {
	return /^\d+$/.test(val);
}

/** 
 * Generate a random id 
 * Used in the academic and school detail pages for ckeditor instances */
function uid() {
	return "id" + Math.random().toString(16).slice(2);
}

/** 
 * Verify if val contains only digits and spaces(and at least one digit)
 * This is the format for price and phone number
 */
function hasOnlySpacesAndDigits(val) {
	return /^(?=.*\d)[\d ]+$/.test(val);
}

/**
 * Verify if username is valid.
 * Username rules:
	- Username should be between 4 to 15 characters and the first 4 characters must be letters.
	- Username should not contain any symbols, dashes or spaces.
	- All other characters are allowed(letters, numbers, hyphens and underscores).
 */
function validateUsername(username) {
	return /^[A-ZÀ-Ÿa-z]{4}[A-ZÀ-Ÿa-z0-9-_]{0,11}$/.test(username);
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
	var usernameOkay = false, phoneNumOkay = false, passwordOkay = false;

	/* Username validation here */
	var username = form.username.value;
	if (!validateUsername(username)) {
		$container.append("<p>" + data.usernameError + "</p>");
	} else {
		usernameOkay = true;
	}

	/* Password validation here  */
	// edit profile form has no password fields so just say its password is okay.
	if (form.name == 'edit-profile-form') {
		passwordOkay = true;
	} else {
		var password = form.password1.value;

		// verify password length and whether password is not entirely numeric
		if (password.length < MIN_PASSWORD_LENGTH || isNumeric(password)) {
			$container.append("<p>" + data.passwordError + "</p>");
		} else {
			passwordOkay = true;
		}
	}

	/* Phone number validation here */
	// validate that numbers are valid(may contain only digits and spaces, no other characters.)
	var $numberInputs = $("tbody .js-number");
	var numbers = [];
	// $numberInputs.each(function(index) {
	// 	var number = this.value;
	// 	// remove all whitespace(space character) from number
	// 	numbers.push(number.replace(/\s/g, ''));
	// });

	$numberInputs.each(function () {
		numbers.push(this.value);
	});

	// test if phone numbers are valid
	phoneNumOkay = true;
	for (var i = 0; i < numbers.length; i++) {
		if (!hasOnlySpacesAndDigits(numbers[i])) {
			phoneNumOkay = false;
			$container.append("<p>" + data.phoneNumError + "</p>");
			// if there is any invalid number, break out of loop
			break;
		}
	}

	/* validate that at least one number supports WhatsApp */
	var $checkboxes = $("tbody .checkboxinput");
	var can_whatsapp_list = [];
	$checkboxes.each(function () {
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
		if (i == phoneNumsCount - 1) {
			phoneNumOkay = false;
			$container.append("<p>" + data.whatsAppError + "</p>");
		}
	}

	// add alert styles if there were any errors
	if (!phoneNumOkay || !passwordOkay || !usernameOkay) {
		e.preventDefault();

		$container.addClass('alert alert-danger');
		alert(data.alertContent);

		// go to top of page so user sees errors
		var topLink = document.querySelector("a[name='top']");
		topLink.click();

		// the previous click appends the hash character ('#') to the url, so remove this character
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
 * Called when user selects another country in the country select menu
 * Also used to fill the city options for the selected country
 */
function insertCities(e) {
	// use this to get value instead of this.value or $(this).val() because 
	// this.value will only work when the select is changed; 
	// but we also want to call this method when the document loads.
	var countryId = parseInt($('.js-country').first().val(), 10);

	// get the select menu containing city options
	var $cityMenu = $('.js-city');

	$.ajax({
		url: e.data.url,
		data: {
			'country_id': countryId
		},
		dataType: 'json',  // data type of the result(response)
		success: function (result) {
			var cities = result['cities'];
			$cityMenu.empty();

			$.each(cities, function (index, item) {
				var option = "<option value=" + item.id + ">" + item.name + "</option>";
				$cityMenu.append(option);
			});
		}
	});
}

/** 
 * Called when user selects another category in the listing category select menu
 * Also used to fill the sub category options for the selected category
 */
function insertItemSubCategories(e) {
	// use this to get value instead of this.value or $(this).val() 
	// because this.value will only work when the select is changed; 
	// but we also want to call this method when the document loads.
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

			$.each(subCategories, function (index, item) {
				var option = "<option value=" + item.id + ">" + item.name + "</option>";
				$subCategoryMenu.append(option);
			});
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
 * If the item condition is new, the condition description field isn't required. 
 otherwise, it is required.
 * Thus make the input field required and append an asterisk to the label.
 */
function onConditionChange(e) {
	var condition = e.target.value;
	var labelText = $('.js-descrLabelText').first().text();
	var labelTextAsterisk = labelText + '*';
	var $conditionDescrInput = $('.js-condition-description').first();
	var $descrLabel = $conditionDescrInput.prev();

	// no condition description required for new item
	if (condition === 'N') {
		$descrLabel.text(labelText);
		$conditionDescrInput.removeAttr('required');
	} else {
		// description required for other items
		$descrLabel.text(labelTextAsterisk);
		$conditionDescrInput.attr('required', '');
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
	$expandedImg.attr({ 'src': img.src, 'alt': img.alt });
}


/** Display toast. Toast should be present in the html page */
function displayToast(type, param) {
	var VALID_TOASTS = [
		'LOGIN_REQUIRED', 'SELF_VOTE', 'ERROR_OCCURRED', 
		'FOLLOW_TOGGLE', 'CUSTOM_SUCCESS', 'CUSTOM_ERROR',
		'BOOKMARK_TOGGLE', 
	];
	if (!VALID_TOASTS.includes(type)) {
		throw `${type} is an invalid toast type`;
	}

	var $myToast, errorCSS = {
		'color': '#842029',
		'border-color': '#f5c2c7',
	};
	
	if (type == 'LOGIN_REQUIRED') {
		$myToast = $('.js-login-required-toast').first();

		// reset styles alert-danger styles since apparently, some toast styles override them. 
		$myToast.css(errorCSS);

	} else if (type == 'SELF_VOTE') {
		$myToast = $('.js-self-vote-toast').first();

		// reset styles alert-danger styles since apparently, some toast styles override them. 
		$myToast.css(errorCSS);

	} else if (type == 'ERROR_OCCURRED') {
		$myToast = $('.js-error-occurred-toast').first();

		// reset styles alert-danger styles since apparently, some toast styles override them. 
		$myToast.css(errorCSS);

	} else if (type == 'BOOKMARK_TOGGLE') {
		var bookmarkAdded = param;
		if (bookmarkAdded)
			$myToast = $('.js-bookmark-added-toast').first();
		else
			$myToast = $('.js-bookmark-removed-toast').first();

	} else if (type == 'FOLLOW_TOGGLE') {
		var followed = param;
		if (followed)
			$myToast = $('.js-followed-toast').first();
		else
			$myToast = $('.js-unfollowed-toast').first();

	} else if (type == 'CUSTOM_SUCCESS') {
		var message = param;
		$myToast = $('.js-custom-success-toast').first();

		var $msgWrp = $('.js-toast-message');
		// use html() not text() 
		$msgWrp.html(message);

	} else if (type == 'CUSTOM_ERROR') {
		var message = param;
		$myToast = $('.js-custom-error-toast').first();

		// reset styles alert-danger styles since apparently, some toast styles override them. 
		$myToast.css(errorCSS);

		var $msgWrp = $('.js-toast-message');
		$msgWrp.html(message);
	}

	var bsToast = new bootstrap.Toast($myToast[0]);
	bsToast.show();
}


/** Attach appropriate events to header dropdown menus based on media type (desktop or mobile) */
function init() {
	var $headerDropdown = $(".js-headerDropdown");
	var $headerAccountInfo = $(".js-headerAccountInfo");

	isMobile = window.matchMedia("only screen and (max-width: 991.98px)").matches;
	var isDesktop = !isMobile;

	// don't enable hover on mobile screens..
	if (isDesktop) {
		// remember login dropdown is only available on desktop
		var $loginDropdown = $(".js-loginDropdown");
		var $deskLangDropdown = $('.js-langDropdownDesk');
		$headerDropdown.hover(headerDropdownHover, headerDropdownMouseLeave);
		$headerDropdown.click(headerDropdownClick);
		$headerAccountInfo.hover(headerAccountInfoHoverOrClick, headerAccountInfoMouseLeave);
		$headerAccountInfo.click(headerAccountInfoHoverOrClick);
		$loginDropdown.hover(loginDropdownHoverOrClick, loginDropdownMouseLeave);
		$loginDropdown.click(loginDropdownHoverOrClick);
		$deskLangDropdown.hover(headerLangDropdownHover, headerLangDropdownMouseLeave);

	} else if (isMobile) {
		// detach all added event handlers and 
		// var Bootstrap default click functionality for dropdowns
		$headerDropdown.off();
		$headerAccountInfo.off();
	}
}

/** Initialize all bootstrap tooltips */
function initTooltips() {
	var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
	var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
		return new bootstrap.Tooltip(tooltipTriggerEl)
	});
}

/**
 * Create and prepare footer select menus
 * Inspired by https://www.w3schools.com/howto/howto_custom_select.asp
 */
function initFooterSelects() {
	function handleSelectClick(e) {
		// when the select box is clicked, close any other select boxes,
		// and open/close the current select box
		e.stopPropagation();
		closeAllFooterSelects(this);
		this.nextSibling.classList.toggle("footer-select--hide");
		this.classList.toggle("footer-select-arrow--active");
	}

	function handleItemClick(e) {
		// when an item is clicked, update the original select box,
		// and the selected item
		var y, i, k, s, h, sl, yl;
		s = this.parentNode.parentNode.getElementsByTagName("select")[0];
		sl = s.length;
		h = this.parentNode.previousSibling;
		for (i = 0; i < sl; i++) {
			if (s.options[i].innerHTML == this.innerHTML) {
				s.selectedIndex = i;
				h.innerHTML = this.innerHTML;
				y = this.parentNode.getElementsByClassName("same-as-selected");
				yl = y.length;
				for (k = 0; k < yl; k++) {
					y[k].classList.remove('same-as-selected')
				}
				this.classList.add("same-as-selected");
				break;
			}
		}
		h.click();
	}

	function handleCountryClick(option, e) {
		// Trigger country form submit
		var select = option.parentElement;
		if (select.selectedIndex != option.index) {
			var countryForm = document.querySelector('#footer-country-form');
			select.selectedIndex = option.index;
			countryForm.submit();
		}
	}

	function handleLangClick(option, e) {
		// Trigger language form submit
		var select = option.parentElement;
		if (select.selectedIndex != option.index) {
			var langForm = document.querySelector('#footer-language-form');
			select.selectedIndex = option.index;
			langForm.submit();
		}
	}

	var x, i, j, l, ll, selElmnt, a, b, c;
	// look for any elements with the class "footer-select-wrp"
	x = document.getElementsByClassName("js-footer-select-wrp");
	l = x.length;

	for (i = 0; i < l; i++) {
		selElmnt = x[i].getElementsByTagName("select")[0];
		ll = selElmnt.length;

		// for each element, create a new DIV that will act as the selected item
		a = document.createElement("DIV");
		a.setAttribute("class", "footer-select-selected");
		a.innerHTML = selElmnt.options[selElmnt.selectedIndex].innerHTML;
		x[i].appendChild(a);

		// for each element, create a new DIV that will contain the option list
		b = document.createElement("DIV");
		b.setAttribute("class", "footer-select-items footer-select--hide");
		for (j = 1; j < ll; j++) {
			// for each option in the original select element,
			// create a new DIV that will act as an option item
			var option = selElmnt.options[j];
			c = document.createElement("DIV");
			c.classList.add('footer-select-items-div');
			c.innerHTML = option.innerHTML;

			if (selElmnt.classList.contains('js-footer-select--country')) {
				c.addEventListener("click", handleCountryClick.bind(this, option));
			} else if (selElmnt.classList.contains('js-footer-select--language')) {
				c.addEventListener('click', handleLangClick.bind(this, option));
			} else {
				c.addEventListener("click", handleItemClick);
			}

			b.appendChild(c);
		}

		x[i].appendChild(b);
		a.addEventListener("click", handleSelectClick);

		// Mark default selected item in list as selected
		// i.e. in list of items, find the currently selected item and mark it as 
		// selected (by adding the 'same-as-selected' class)
		var idx;
		var sd = x[i].getElementsByClassName('footer-select-items-div');
		for (idx = 0; idx < sd.length; idx++) {
			// Use -1 because in the select menu, the initial option is present twice
			if (selElmnt.selectedIndex - 1 == idx) {
				sd[idx].classList.add("same-as-selected");
				break;
			}
		}
	}
}

/**
 * Close footer select menus
 */
function closeAllFooterSelects(elmnt) {
	/*a function that will close all select boxes in the document,
	except the current select box:*/
	var x, y, i, xl, yl, arrNo = [];
	x = document.getElementsByClassName("footer-select-items");
	y = document.getElementsByClassName("footer-select-selected");
	xl = x.length;
	yl = y.length;

	for (i = 0; i < yl; i++) {
		if (elmnt == y[i]) {
			arrNo.push(i)
		} else {
			y[i].classList.remove("footer-select-arrow--active");
		}
	}

	for (i = 0; i < xl; i++) {
		if (arrNo.indexOf(i)) {
			x[i].classList.add("footer-select--hide");
		}
	}
}


$window.on('resize', function () {
	var $this = $(this);
	var newWidth = $this.width();
	if (newWidth !== lastWidth) {
		lastWidth = newWidth;
		// console.log(lastWidth);
		init();
	}
});


$(document).ready(function () {
	init();
	initTooltips();
	initFooterSelects();
	lastWidth = $window.width();
});


/** BOOKMARKING  */
// some variables used here are defined in the bookmarking.html file.

$('.js-bookmark-button').click(function (event) {
	// if user isn't logged in
	if (!userId) {
		displayToast('LOGIN_REQUIRED');
		return false;
	}

	var $this = $(this);
	var $icon = $this.children('i'), id = parseInt(this.dataset.id, 10);

	// if user is trying to undo the bookmark
	if ($icon.hasClass('js-selected')) {
		var voteAction = 'recall-bookmark';

		$.ajax({
			url: bookmarkUrl,
			type: 'POST',
			data: { id: id, action: voteAction },
			dataType: 'json',
			beforeSend: function (xhr) {
				xhr.setRequestHeader("X-CSRFToken", csrfToken);
			},
			success: function (result) {
				if (result['unbookmarked']) {
					// remove fas(font-awesome solid) class and set to far(font-awesome regular)
					$icon.removeClass('fas js-selected').addClass('far');

					// update bookmark count
					var newCount = parseInt($bookmarkCounter.text(), 10);
					$bookmarkCounter.text(newCount - 1);

					// update text
					var textNode = $icon[0].nextSibling;
					textNode.textContent = " " + bookmarkText;
					displayToast('BOOKMARK_TOGGLE', false);

				} else {
					console.error(result);
					displayToast('ERROR_OCCURRED');
				}
			}
		});

	} else {
		// if user is adding a new bookmark
		var voteAction = 'bookmark';

		$.ajax({
			url: bookmarkUrl,
			type: 'POST',
			data: { id: id, action: voteAction },
			dataType: 'json',
			beforeSend: function (xhr) {
				xhr.setRequestHeader("X-CSRFToken", csrfToken);
			},
			success: function (result) {
				if (result['bookmarked']) {
					// remove far class and set to fas
					$icon.removeClass('far').addClass('fas js-selected');

					// update bookmark count
					var newCount = parseInt($bookmarkCounter.text(), 10);
					$bookmarkCounter.text(newCount + 1);

					var textNode = $icon[0].nextSibling;
					textNode.textContent = " " + bookmarkedText;
					displayToast('BOOKMARK_TOGGLE', true);
				} else {
					console.error(result);
					displayToast('ERROR_OCCURRED');
				}
			}
		});
	}
});


/** FLAGGING */
document.addEventListener('DOMContentLoaded', function () {
	'use strict';

	var headers = {
		'X-Requested-With': 'XMLHttpRequest',
		'Content-Type': 'application/x-www-form-urlencoded'
	};

	const fadeOut = function (element, duration) {
		var interval = 10;//ms
		var opacity = 1.0;
		var targetOpacity = 0.0;
		var timer = setInterval(function () {
			if (opacity <= targetOpacity) {
				opacity = targetOpacity;
				clearInterval(timer);
			}
			element.style.opacity = opacity;
			opacity -= 1.0 / ((1000 / interval) * duration);
		}, interval);
	};

	const fadeIn = function (element, duration) {
		var interval = 20;//ms
		var opacity = 0.0;
		var targetOpacity = 1.0;
		var timer = setInterval(function () {
			if (opacity >= targetOpacity) {
				opacity = targetOpacity;
				clearInterval(timer);
			}
			element.style.opacity = opacity;
			opacity += 1.0 / ((1000 / interval) * duration);
		}, interval);
	};

	const toggleClass = function (element, addClass, removeClass, action) {
		if (action === 'add') {
			element.classList.add(...addClass);
			element.classList.remove(...removeClass);
		} else {
			element.classList.remove(...addClass);
			element.classList.add(...removeClass);
		}
	};

	const toggleText = function (element, action) {
		// element that contains flag 
		// const spanEle = element.querySelector('span');
		// var textSpan = spanEle.querySelector('span');
		var textSpan = (document.querySelector('.js-first-child')).previousElementSibling;

		// `textSpan` will be null if no text is present. 
		// (such as flags near comments where no text is present)
		if (textSpan) {
			if (action == 'add') {
				var text = document.querySelector('.js-remove-flag').textContent;
				textSpan.textContent = text;
			} else {
				var text = document.querySelector('.js-report-content').textContent;
				textSpan.textContent = text;
			}
		}
	};

	const toggleTitle = function (element, action) {
		// element that contains flag 
		const spanEle = element.querySelector('span');

		// if element previously had a title, update the title
		if (spanEle.hasAttribute('title')) {
			if (action == 'add') {
				var text = document.querySelector('.js-remove-flag').textContent;
				spanEle.setAttribute('title', text);
			} else {
				var text = document.querySelector('.js-report-content').textContent;
				spanEle.setAttribute('title', text);
			}
		}
	};

	const createInfoElement = function (responseEle, status, msg, duration = 2) {
		switch (status) {
			case -1:
				status = "danger";
				break;
			case 0:
				status = "success";
				break;
			case 1:
				status = "warning";
				break;
		}
		const cls = 'alert-' + status;
		const temp = document.createElement('div');
		temp.classList.add('h6');
		temp.classList.add('alert');
		temp.classList.add(cls);
		temp.innerHTML = msg;
		responseEle.prepend(temp);
		fixToTop(temp);
		fadeIn(temp, duration);
		setTimeout(() => {
			fadeOut(temp, duration);
		}, duration * 1000);

		setTimeout(() => {
			temp.remove();
		}, 2000 * duration);
	};

	const fixToTop = function (div) {
		const top = 200;
		const isFixed = div.style.position === 'fixed';
		if (div.scrollTop > top && !isFixed) {
			div.setAttribute('style', "{'position': 'fixed', 'top': '0px'}");
		}
		if (div.scrollTop < top && isFixed) {
			div.setAttribute('style', "{'position': 'static', 'top': '0px'}");
		}

	};

	const hideModal = function (modal) {
		modal.style.display = 'none';
		modal.querySelector('form').reset();
		modal.querySelector('textarea').style.display = 'none';
	};

	const showModal = function (e) {
		const modal = e.currentTarget.nextElementSibling;
		modal.style.display = "block";
	};

	const removeFlag = function (e) {
		submitFlagForm(e.currentTarget, 'remove');
	};

	const convertDataToURLQuery = function (data) {
		return Object.keys(data).map(function (key) {
			return encodeURIComponent(key) + '=' + encodeURIComponent(data[key]);
		}).join('&');
	};

	const submitFlagForm = function (ele, action = 'add') {
		var flagEle, info = null, reason = null;

		if (action !== 'add') {
			action = 'remove';
			flagEle = ele;
		} else {
			flagEle = ele.closest('.report-modal-form-combined').firstElementChild;
			reason = ele.querySelector('input[name="reason"]:checked').value;
			info = ele.querySelector('textarea').value;
		}
		const url = flagEle.getAttribute('data-url');
		const appName = flagEle.getAttribute('data-app-name');
		const modelName = flagEle.getAttribute('data-model-name');
		const modelId = flagEle.getAttribute('data-model-id');
		const csrf = flagEle.getAttribute('data-csrf');
		const data = {
			'app_name': appName,
			'model_name': modelName,
			'model_id': modelId,
		};
		if (reason) { data['reason'] = reason; };
		if (info) { data['info'] = info; };

		const query = convertDataToURLQuery(data);
		headers['X-CSRFToken'] = csrf;
		fetch(url, {
			'method': 'post',
			'headers': headers,
			'body': query,
		}).then(function (response) {
			return response.json();
		}).then(function (response) {
			const addClass = ['user-has-flagged', 'fas'];
			const removeClass = ['user-has-not-flagged', 'far'];
			const flagIcon = flagEle.querySelector('.flag-icon');

			if (response) {
				createInfoElement(flagEle.parentElement, response.status, response.msg);
				const modal = flagEle.nextElementSibling;
				var action;
				if (response.flag === 1) {
					action = 'add';
					hideModal(modal);
					flagEle.removeEventListener('click', showModal);
					flagEle.addEventListener('click', removeFlag);
				} else {
					action = 'remove';
					flagEle.removeEventListener('click', removeFlag);
					flagEle.addEventListener('click', showModal);
					prepareFlagModal(flagEle);
				}

				toggleClass(flagIcon, addClass, removeClass, action);
				toggleText(flagEle, action);
				toggleTitle(flagEle, action);
			}
		}).catch(function (error) {
			console.error(error);

			// get flag error message
			var alertMsg = document.querySelector('.js-flag-alert-msg').textContent;
			// Note: toast(.js-custom-error-toast) must be in html 
			displayToast('CUSTOM_ERROR', alertMsg);
		});
	};

	const prepareFlagModal = function (flagEle, parent=null) {
		if (!parent) {
			parent = flagEle.nextElementSibling.parentElement;
		}

		const modal = parent.querySelector('.flag-report-modal');
		flagEle.addEventListener('click', showModal);

		const span = parent.querySelector(".report-modal-close");
		span.onclick = function () {
			hideModal(modal);
		};

		// when the user clicks on the last reason , open the info box
		const flagForm = parent.querySelector('.report-modal-form');
		const lastFlagReason = flagForm.querySelector('.last-flag-reason');
		const flagInfo = flagForm.querySelector('.report-modal-form-info');
		flagForm.onchange = function (event) {
			// Display info textarea if last input checkbox was clicked or last focus
			// was from textarea
			if (event.target.value === lastFlagReason.value || event.target == flagInfo) {
				flagInfo.required = true;
				flagInfo.style.display = "block";
				flagInfo.focus();
			} else {
				flagInfo.style.display = "none";
				flagInfo.removeAttribute('required');  
			}
		};

		// add flag
		flagForm.onsubmit = function (event) {
			event.preventDefault();
			submitFlagForm(flagForm, 'add');
		};
	};

	const parents = document.getElementsByClassName("report-modal-form-combined");
	for (const parent of parents) {
		const modal = parent.querySelector('.flag-report-modal');
		// When the user clicks anywhere outside of the main modal, close it.
		window.onclick = function (event) {
			// modal will be full width so we know target will be from modal
			if (event.target == modal) {
				hideModal(modal);
			}
		};

		const flagEle = parent.querySelector(".flag-report-icon");
		const flagIcon = flagEle.querySelector('.flag-icon');
		if (flagIcon.classList.contains('user-has-not-flagged')) {
			prepareFlagModal(flagEle, parent);
		} else {
			flagEle.addEventListener('click', removeFlag);
		}
	};
});


// iF the user clicks anywhere outside the select box,
// then close all footer select boxes
document.addEventListener("click", function (e) {
	closeAllFooterSelects();
});
