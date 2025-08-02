$(function() {
    $('body').on("click", "a.rqlio", function(ev) {
    	ev.preventDefault(); // do not follow the a link
    	var payload = [[$(this).data('rql'), null]];
    	$.ajax(this.href, {method: 'POST',
    			   contentType: 'application/json',
    			   data: JSON.stringify(payload)})
    	    .done(function() {
    		document.location.reload(true);
    	    });
    	return false;
    });
});
