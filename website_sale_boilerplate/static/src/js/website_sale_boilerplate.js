
// On change hide add_to_cart
function toggle_visibility(id) {
   var e = document.getElementById(id);
   if(e.style.display == 'block')
      e.style.display = 'none';
   else
      e.style.display = 'block';
}

// Quit Checked box
$(document).on('click', '.js_add_cart_variants', function(e) {
    var elem = document.getElementById('visible_cart_check');
    var elem2 = document.getElementById('visible_cart_label');
    if(elem.checked)
      elem2.click();
});
