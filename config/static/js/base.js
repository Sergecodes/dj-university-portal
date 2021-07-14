'use strict';

var NAV_LINK_ACTIVE_COLOR = '#0e1e0a';
var $window = $(window);
var windowWidth = $window.width();
var isMobile = window.matchMedia("only screen and (max-width: 991.98px)").matches;


function headerDropdownHover() {
  var dropdownMenu = $(this).children(".dropdown-menu");
  dropdownMenu.show();

  var navLink = $(this).find("> a:first-child");
  navLink.css('color', NAV_LINK_ACTIVE_COLOR);
  navLink.attr('aria-expanded', 'true');

  if(dropdownMenu.is(":visible")) {
    dropdownMenu.parent().toggleClass("show");
  }
}

function headerDropdownClick() {
  var dropdownMenu = $(this).children(".dropdown-menu");
  dropdownMenu.show();
  var navLink = $(this).find("> a:first-child");
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

  var navLink = $(this).find("> a:first-child");
  navLink.css('color', 'white');
  navLink.attr('aria-expanded', 'false');
}

function headerAccountInfoHoverOrClick(event) {
  var dropdownMenu = $(this).find('> .dropdown-menu-end');
  dropdownMenu.addClass("show");
  dropdownMenu.show();
  dropdownMenu.css({
    'position': 'absolute',
    'inset': '0px auto auto 0px',
    'margin': '0px',
    'transform': 'translate(-96px, 67px)'
  });

  var link = $(this).find("> a:first-child");
  link.attr('aria-expanded', 'true');
  link.css('filter', 'drop-shadow(rgba(255, 255, 255, 0.5) 0px 2px 5px)');
}

function headerAccountInfoMouseLeave() {
  // var dropdownMenu = $(this).children('.dropdown-menu-end');
  var dropdownMenu = $(this).find('> .dropdown-menu-end');
  dropdownMenu.removeClass("show");
  dropdownMenu.hide();

  var link = $(this).find("> a:first-child");
  link.attr('aria-expanded', 'false');
  link.css('filter', '');
}

function init() {
  var $headerDropdown = $(".js-headerDropdown");
  var $headerAccountInfo = $(".js-headerAccountInfo");
  isMobile = window.matchMedia("only screen and (max-width: 991.98px)").matches;
  var isDesktop = !isMobile;

  // don't enable hover on mobile screens..
  if (isDesktop) {
    $headerDropdown.hover(headerDropdownHover, headerDropdownMouseLeave);
    $headerDropdown.click(headerDropdownClick);
    $headerAccountInfo.hover(headerAccountInfoHoverOrClick, headerAccountInfoMouseLeave);
    $headerAccountInfo.click(headerAccountInfoHoverOrClick);

  } else if (isMobile) {
    // detach all event handlers and let Bootstrap default click functionality for dropdowns
    $headerDropdown.off();
    $headerAccountInfo.off();
  }
}

$window.on('resize', function() {
  var $this = $(this);
  if ($this.width() !== windowWidth) {
    windowWidth = $this.width();
    console.log(windowWidth);
    init();
  }
});

// window.addEventListener('resize', function(event) {
//   console.log("window resized");
//   init();
//
// });

$(document).ready(function() {
  init();

});
