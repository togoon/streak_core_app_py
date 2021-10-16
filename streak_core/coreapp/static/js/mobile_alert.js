$(document).ready(function(){
	$(".loader_parent").fadeOut();
	// fetch_notifications();
	// refresh_notification();
	// notifications_read();
	$("#logo_link").find("img").attr("src", "/static/imgs/logosvg.svg");


});

// function update_android_session(user_is_auth,id){
// 	try{
// 		Android.createUserSession(user_is_auth,id);
// 		Android.showToast("Logged in");
//     }
//     catch(e){
// 		console.log(e);
//     }
// }

// function remove_android_session(){
// 	try{
// 		Android.removeUserSession();
//     }
//     catch(e){
// 		console.log(e);
//     }
// }