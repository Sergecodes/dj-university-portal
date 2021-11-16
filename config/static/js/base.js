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


function headerDropdownHover() {
	var dropdownMenu = $(this).children(".dropdown-menu");
	dropdownMenu.show();

	var $navLink = $(this).children("a:first-child");
	
	// if nav link isn't for current page, set color...
	if (!$navLink.hasClass(CURRENT_NAV_LINK_CLASS)) {
		$navLink.css('color', NAV_LINK_ACTIVE_COLOR);
	}
	$navLink.attr('aria-expanded', 'true');

	if(dropdownMenu.is(":visible")) {
		dropdownMenu.parent().toggleClass("show");
	}
}


function headerDropdownClick() {
	var dropdownMenu = $(this).children(".dropdown-menu");
	dropdownMenu.show();
	var $navLink = $(this).children("a:first-child");

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


function headerDropdownMouseLeave(event) {
	var dropdownMenu = $(this).children(".dropdown-menu");
	dropdownMenu.hide();

	var $navLink = $(this).children("a:first-child");

	// if nav link isn't for current page, set color to white(default)
	if (!$navLink.hasClass(CURRENT_NAV_LINK_CLASS)) {
		$navLink.css('color', 'white');
	}
	$navLink.attr('aria-expanded', 'false');
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
 * Verify if full name is valid.
 * Full name rules:
	- Full name can contain only letters and hyphens.
	- It consists of two or three names separated by space(s).
	- Shouldn't start or end with hyphens and no name should contain only hyphens
 */
function validateFullName(fullName) {
	return /^(?:[A-ZÀ-Ÿa-z]+(?:-[A-ZÀ-Ÿa-z]+)*)+[\s]+(?:[A-ZÀ-Ÿa-z]+(?:-[A-ZÀ-Ÿa-z]+)*)+[\s]*(?:[A-ZÀ-Ÿa-z]+(?:-[A-ZÀ-Ÿa-z]+)*)*$/.test(fullName);
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
	var usernameOkay = false, fullNameOkay = false;
	var phoneNumOkay = false, passwordOkay = false;

	/* Full name validation here */
	var fullName = form.full_name.value;
	if (!validateFullName(fullName)) {
		$container.append("<p>" + data.fullNameError + "</p>");
	} else {
		fullNameOkay = true;
	}

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

	$numberInputs.each(function() {
		numbers.push(this.value);
	});

	// test if phone numbers are valid
	phoneNumOkay = true;
	for (var i = 0; i < numbers.length; i++) {
		if(!hasOnlySpacesAndDigits(numbers[i])) {  
			phoneNumOkay = false;
			$container.append("<p>" + data.phoneNumError + "</p>");
			// if there is any invalid number, break out of loop
			break;
		}
	}

	/* validate that at least one number supports WhatsApp */
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
	if (!phoneNumOkay || !passwordOkay || !fullNameOkay || !usernameOkay) {
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
 */
 function displayBookmarkToggleToast(bookmarkAdded) {
	var $myToast;
	if (bookmarkAdded) 
		$myToast = $('.js-bookmark-added-toast').first();
	else 
		$myToast = $('.js-bookmark-removed-toast').first();

	var bsToast = new bootstrap.Toast($myToast[0]);
	bsToast.show(); 
}


/**
 * Display toast telling user that they have successfully followed or unfollowed a post
 * Toast should be present in the html page
 */
 function displayFollowToggleToast(followed) {
	var $myToast;
	if (followed) 
		$myToast = $('.js-followed-toast').first();
	else 
		$myToast = $('.js-unfollowed-toast').first();

	var bsToast = new bootstrap.Toast($myToast[0]);
	bsToast.show(); 
}


/**
 * Display custom success message toast
 * Toast should be present in the html page
 */
 function displayCustomSuccessToast(message) {
	// this toast should be present in the html page !
	var $myToast = $('.js-custom-success-toast').first();

	var $msgWrp = $('.js-toast-message');
	// use html() not text() 
	$msgWrp.html(message);

	var bsToast = new bootstrap.Toast($myToast[0]);
	bsToast.show(); 
}


/**
 * Display custom error message toast
 * Toast should be present in the html page
 */
 function displayCustomErrorToast(message) {
	// this toast should be present in the html page !
	var $myToast = $('.js-custom-error-toast').first();

	// reset styles alert-danger styles since apparently, some toast styles override them. 
	$myToast.css({
		'color': '#842029',
		'border-color': '#f5c2c7'
	});

	var $msgWrp = $('.js-toast-message');
	// use html() not text() 
	$msgWrp.html(message);

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
		$headerDropdown.hover(headerDropdownHover, headerDropdownMouseLeave);
		$headerDropdown.click(headerDropdownClick);
		$headerAccountInfo.hover(headerAccountInfoHoverOrClick, headerAccountInfoMouseLeave);
		$headerAccountInfo.click(headerAccountInfoHoverOrClick);
		$loginDropdown.hover(loginDropdownHoverOrClick, loginDropdownMouseLeave);
		$loginDropdown.click(loginDropdownHoverOrClick);

	} else if (isMobile) {
		// detach all added event handlers and 
		// let Bootstrap default click functionality for dropdowns
		$headerDropdown.off();
		$headerAccountInfo.off();
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

	// var $languageSelect = $(".js-languageSelect");
	// $languageSelect.on('change', function() {
	// 	$(this).closest('form').submit();
	// });

});


/** BOOKMARKING  */
// some variables used here are defined in the bookmarking.html file.

$('.js-bookmark-button').click(function(event) {
    // if user isn't logged in
    if (!userId) {
        displayLoginRequiredToast();
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
            data: {id: id, action: voteAction},
            dataType: 'json',
            beforeSend: function (xhr) {
                xhr.setRequestHeader("X-CSRFToken", csrfToken);
            },
            success: function(result) {
                if (result['unbookmarked']) {
                    // remove fas(font-awesome solid) class and set to far(font-awesome regular)
                    $icon.removeClass('fas js-selected').addClass('far');

                    // update bookmark count
                    var newCount = parseInt($bookmarkCounter.text(), 10);
                    $bookmarkCounter.text(newCount - 1);

                    // update text
                    var textNode = $icon[0].nextSibling;
                    textNode.textContent = " " + bookmarkText;
                    displayBookmarkToggleToast(false);

                } else {
                    console.error(result);
                    displayErrorOccurredToast();
                }
            }
        });

    } else {
        // if user is adding a new bookmark
        var voteAction = 'bookmark';

        $.ajax({
            url: bookmarkUrl,
            type: 'POST',
            data: {id: id, action: voteAction},
            dataType: 'json',
            beforeSend: function (xhr) {
                xhr.setRequestHeader("X-CSRFToken", csrfToken);
            },
            success: function(result) {
                if (result['bookmarked']) {
                    // remove far class and set to fas
                    $icon.removeClass('far').addClass('fas js-selected');

                    // update bookmark count
                    var newCount = parseInt($bookmarkCounter.text(), 10);
                    $bookmarkCounter.text(newCount + 1);

                    var textNode = $icon[0].nextSibling;
                    textNode.textContent = " " + bookmarkedText;
                    displayBookmarkToggleToast(true);
                } else {
                    console.error(result);
                    displayErrorOccurredToast();
                }
            }
        });
    }
});


/** FLAGGING */
document.addEventListener('DOMContentLoaded', function () {
	'use strict';
  
	let headers = {
	  'X-Requested-With': 'XMLHttpRequest',
	  'Content-Type': 'application/x-www-form-urlencoded'
	};
  
	const fadeOut = function (element, duration) {
	  let interval = 10;//ms
	  let opacity = 1.0;
	  let targetOpacity = 0.0;
	  let timer = setInterval(function () {
		if (opacity <= targetOpacity) {
		  opacity = targetOpacity;
		  clearInterval(timer);
		}
		element.style.opacity = opacity;
		opacity -= 1.0 / ((1000 / interval) * duration);
	  }, interval);
	};
  
	const fadeIn = function (element, duration) {
	  let interval = 20;//ms
	  let opacity = 0.0;
	  let targetOpacity = 1.0;
	  let timer = setInterval(function () {
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
	  const spanEle = element.querySelector('span');
	  var textSpan = spanEle.querySelector('span');
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
	  let flagEle, info = null, reason = null;
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
		  let action;
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
		displayCustomErrorToast(alertMsg);
	  });
	};
  
	const prepareFlagModal = function (flagEle, parent = null) {
	  if (!parent) {
		parent = flagEle.nextElementSibling.parentElement;
	  };
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
		if (event.target.value === lastFlagReason.value) {
		  flagInfo.required = true;
		  flagInfo.style.display = "block";
		} else {
		  flagInfo.style.display = "none";
		  flagInfo.removeAttribute('required');  // added. 
		};
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
	  // When the user clicks anywhere outside of the modal, close it
	  window.onclick = function (event) {
		if (event.target == modal) {
		  hideModal(modal);
		};
	  };
  
	  const flagEle = parent.querySelector(".flag-report-icon");
	  const flagIcon = flagEle.querySelector('.flag-icon');
	  if (flagIcon.classList.contains('user-has-not-flagged')) {
		prepareFlagModal(flagEle, parent);
	  } else {
		flagEle.addEventListener('click', removeFlag);
	  };
	};
  });
  