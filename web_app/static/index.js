$(document).ready(function() {
	$('.toggler').click(function() {
		if ($('.hide_seek').hasClass('hide')){
		  $('.toggler').text("Hide Recommendations");
		  $('.hide_seek').removeClass('hide');
		}else{
  		  $('.toggler').text("Show Recommendations");
  		  $('.hide_seek').addClass('hide');
		}
	});
});
