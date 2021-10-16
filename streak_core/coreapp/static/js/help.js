// $(document).ready(function(){
// 	$(".loader_parent").fadeOut();
// });
$(window).load(function() {
    // Animate loader off screen
    $(".loader_parent").fadeOut();
    show_methodology();
});
function show_help(){
    $("#faq, #methodology").hide();
    $("#help").show();
    $("#faq_option, #methodology_option").removeClass("help_page_options_menu_selected");
    $("#help_option").addClass("help_page_options_menu_selected");
}
function show_faq(){
	$("#help, #methodology").hide();
    $("#faq").show();
    $("#help_option, #methodology_option").removeClass("help_page_options_menu_selected");
    $("#faq_option").addClass("help_page_options_menu_selected");
}
function show_methodology(){
	$("#help, #faq").hide();
    $("#methodology").show();
    $("#help_option, #faq_option").removeClass("help_page_options_menu_selected");
    $("#methodology_option").addClass("help_page_options_menu_selected");
}
$(document).ready(function(){
    if(window.location.href.indexOf('#help')!=-1)
    {
        show_help();
    }
    $("#help_option").click(function(){
        show_help(); 
    });
    $("#faq_option").click(function(){
        show_faq();
    });
    $("#methodology_option").click(function(){
        show_methodology();
    });
});