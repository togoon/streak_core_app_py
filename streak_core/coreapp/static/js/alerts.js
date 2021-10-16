$(document).ready(function(){
	$(".loader_parent").fadeOut();
	// fetch_notifications();
	// refresh_notification();
	// notifications_read();
	$('#notif_count').text(0);
    $('#notif_count').hide(); 
    // ajax to mark all notifications as read
    notifications_read();  
});