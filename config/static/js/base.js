
$(document).ready(function() {
    var $submitIcon = $('.js-header-search-form__icon-wrapper');
    var $inputBox = $('.js-header-search-form__input');
    var $searchBox = $('.js-header-search-form');
    var isOpen = false;

    $submitIcon.click(function() {
        if(isOpen == false) {
            $searchBox.addClass('header-search-form--open');
            $inputBox.focus();
            isOpen = true;
        } else {
            $searchBox.removeClass('header-search-form--open');
            $inputBox.focusout();
            isOpen = false;
        }
    });

    $submitIcon.mouseup(function() {
        return false;
    });

    $searchBox.mouseup(function() {
        return false;
    });

    /* To see if a click took place outside the search box */
    $(document).mouseup(function() {
        console.log('click outside search');
        if(isOpen == true) {
            $submitIcon.css('display', 'block');
            $submitIcon.click();
        }
    });
});

function headerSearchButtonUp() {
    var inputVal = $('.js-header-search-form__input').val();
    inputVal = $.trim(inputVal).length;

    if(inputVal !== 0) {
        $('.js-header-search-form__icon-wrapper').css('display', 'none');
    } else {
        $('.js-header-search-form__input').val('');
        $('.js-header-search-form__icon-wrapper').css('display', 'block');
    }
}

