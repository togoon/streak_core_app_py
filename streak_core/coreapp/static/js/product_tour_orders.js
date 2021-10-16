 $(document).ready(function(){
 // Define the tour!
    
    // if (first_time_orders == "true"){
    //   hopscotch.startTour(tour);
    // }
});
 function orders_tour(){
 var tour = {
      id: "hello-hopscotch",
      steps: [
        {
          title: "Waiting",
          content: "Shows all the strategies that have been deployed and are waiting for the first trigger event.",
          target: "waiting_option",
          placement: "bottom",
          showCloseButton: true
        },
        {
          title: "Entered",
          content: "Shows all the strategies that you have taken a position and are waiting for an exit condition/ stop loss/ target profit event.",
          target: "entered_option",
          placement: "bottom",
          showPrevButton: true
        },
        {
          title: "Stopped",
          content: "Shows all the strategies that have been stopped by you or auto-terminated or completed.",
          target: "stopped_option",
          placement: "bottom",
          showPrevButton: true
        },
        {
          title: "Search strategies",
          content: "Search strategies using the strategy name.",
          target: document.querySelector(".search_refresh_container"),
          placement: "left",
          showPrevButton: true
        },
        {
          title: "Refresh",
          content: "Click to refresh.",
          target: document.querySelector(".refresh_bar"),
          placement: "left",
          showPrevButton: true
        },
        {
          title: "Manage strategies",
          content: "Click on the blue dots to stop strategy, view orderlog, view strategy details and re-deploy strategy.",
          target: document.querySelector(".menu_dots"),
          placement: "left",
          showPrevButton: true
        }
      ]
    };
    return tour;
 }