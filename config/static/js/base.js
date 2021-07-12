var NAV_LINK_ACTIVE_COLOR = '#0e1e0a';


$(document).ready(function() {
  var $headerDropdown = $(".js-headerDropdown");

  $headerDropdown.hover(function(){
    var dropdownMenu = $(this).children(".dropdown-menu");
    dropdownMenu.show();

    var navLink = $(this).find("> :first-child");
    navLink.css('color', NAV_LINK_ACTIVE_COLOR);
    navLink.attr('aria-expanded', 'true');

    if(dropdownMenu.is(":visible")) {
      dropdownMenu.parent().toggleClass("show");
    }
  });

  $headerDropdown.on({
    mouseleave: function() {
      var dropdownMenu = $(this).children(".dropdown-menu");
      dropdownMenu.hide();

      var navLink = $(this).find("> :first-child");
      navLink.css('color', 'white');
      navLink.attr('aria-expanded', 'false');
    },
    click: function() {
      var dropdownMenu = $(this).children(".dropdown-menu");
      dropdownMenu.show();
      var navLink = $(this).find("> :first-child");
      navLink.css('color', NAV_LINK_ACTIVE_COLOR);
      navLink.attr('aria-expanded', 'true');

      // remove boostrap styles on visible dropdowns, these styles are applied to the style attribute
      dropdownMenu.css({
        'position': '',
        'inset': '',
        'margin': '',
        'transform': ''
      });
    }
  });

  // $('#buySellItem, #askQuestion, #classroom, #change, #socialize').off('click');
  // $headerDropdown.on('click mouseleave', function(e) {
  //   // e.type is the type of event fired
  //   var dropdownMenu = $(this).children(".dropdown-menu");
  //   console.log(e.type);
  //   if (e.type == "mouseleave") {
  //     // dropdownMenu.css('display', 'none');
  //     dropdownMenu.hide();
  //   }
  //   // else if (e.type == "click") {
  //   //   // remove boostrap styles on visible dropdowns, these styles are applied to the style attribute
  //   //   dropdownMenu.css({
  //   //     'position': '',
  //   //     'inset': '',
  //   //     'margin': '',
  //   //     'transform': ''
  //   //   });
  //   // }
  //
  // });


  $(".js-headerAccountInfo").hover(function() {
    var dropdownMenu = $(this).children('.dropdown-menu-end');
    if(dropdownMenu.is(":visible")) {
      dropdownMenu.toggleClass("show");
      dropdownMenu.css({
        'position': 'absolute',
	      'inset': '0px auto auto 0px',
        'margin': '0px',
        'transform': 'translate(-96px, 67px)'
      });
    }
  });

});
