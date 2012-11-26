//small placeholders help_script for support older browsers (IE9 etc.)
// XXX: Should be removed as soon as ie9 support is dropped.

$(document).ready(function(){
  function add() {
      if($(this).val() == ''){
          $(this).val($(this).attr('placeholder')).addClass('placeholder');
      }
  }

  function remove() {
      if($(this).val() == $(this).attr('placeholder')){
          $(this).val('').removeClass('placeholder');
      }
  }

  // Create a dummy element for feature detection
  if (!('placeholder' in $('<input>')[0])) {

      // Select the elements that have a placeholder attribute
      $('input[placeholder], textarea[placeholder]').blur(add).focus(remove).each(add);

      // Remove the placeholder text before the form is submitted
      $('form').submit(function(){
          $(this).find('input[placeholder], textarea[placeholder]').each(remove);
      });
  }
});
