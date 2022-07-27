/** 
 * This contains code that will be run alongside selectize.js
 * Also, updating the options in the widget doesn't seem to work, 
 * so we'll just do it here.
 */
// $select is defined in the qa_site.widgets.render method

// document.load won't work. Use window.load so as to wait for all 
// files to be loaded before getting the variable.
$(window).on('load', function () {
   var selectize = $select.prevObject[0].selectize;
   const invalidChars = "\"'\|`~!@#$%^&*()}{_+=,<>/?;:";
   console.log(selectize);

   selectize.settings.maxItems = 5;

   // Also use comma as delimiter
   // github.com/selectize/selectize.js/issues/674#issuecomment-142180431
   selectize.on('type', function(str) {
      var delimiter2 = ',';
      if (str.slice(-1) === delimiter2) {
         this.createItem(str.slice(0, -1));
         // in case user enters just the delimiter, remove it
         this.removeItem(delimiter2); 
      }
   });

   // Validate characters
   selectize.settings.createFilter = function (text) {
      var n = text.length;
      var newChar = text.at(-1);
      if (invalidChars.includes(newChar)) {
         // Remove character 
         selectize.setTextboxValue(text.substring(0, n-1));
         return false;
      }

      return true;
   }

   /* See how its done in selectize.js */
   selectize.onKeyDown = (function() {
      // First get previous onKeyDown property
      var original = selectize.onKeyDown;

      return function(e) {
         var text = e.target.value;
         var n = text.length;
         var newChar = text.at(-1);
         
         if (invalidChars.includes(newChar)) {
            // Remove character 
            selectize.setTextboxValue(text.substring(0, n-1));
            return false;
         }

         return original.apply(this, arguments);
      };
   })();

});

