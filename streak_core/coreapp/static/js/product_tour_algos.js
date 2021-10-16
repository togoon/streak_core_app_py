 $(document).ready(function(){
 // Define the tour!
    // var tour = {
    //   id: "hello-hopscotch",
    //   steps: [
    //     {
    //       title: "Algos",
    //       content: "This section shows the algos you have created and the details",
    //       target: document.querySelector("#algo_name"),
    //       placement: "right",
    //       showCloseButton: true
    //     },
    //     {
    //       title: "Latest backtests and live algos",
    //       content: "A snapshot of the most recent backtests and any deployed algos",
    //       target: "dashboard_equities_section",
    //       placement: "left",
    //       showPrevButton: true
    //     },
    //     {
    //       title: "Results",
    //       content: "Click here to view the detailed backtest results",
    //       target: document.querySelector("#icon-dashboard-backtest"),
    //       placement: "bottom",
    //       showPrevButton: true
    //     },
    //     {
    //       title: "Edit algo",
    //       content: "You will be taken to the edit algo page.",
    //       target: document.querySelector("#icon-edit"),
    //       placement: "bottom",
    //       showPrevButton: true
    //     },
    //     {
    //       title: "Deploy",
    //       content: "Take your algo live in the market via Zerodha. Deploying will activate actionable alerts for entry and exit signals as per your algo.",
    //       target: document.querySelector("#deploy"),
    //       placement: "left",
    //       showPrevButton: true
    //     },
    //     {
    //       title: "Force stop",
    //       content: "This will stop your algo and you will not receive further alerts.",
    //       target: document.querySelector("#force_stop"),
    //       placement: "left",
    //       showPrevButton: true
    //     },
    //     {
    //       title: "Order tree",
    //       content: "Click here to see the tree of events that have occured since deploying your algo for this equity",
    //       target: "view_od",
    //       placement: "left",
    //       showPrevButton: true
    //     }
    //   ]
    // };
    if (first_time_algos == "true"){
      hopscotch.startTour(algos_tour());
    }
    $("#take_tour, #take_tour_mobile").click(function(){
      hopscotch.startTour(algos_tour());
    });
});
function algos_tour(){
  var algos_tour = {
      id: "hello-hopscotch",
      steps: [
        {
          title: "Strategies",
          content: "List of all strategies you have created and their details.",
          target: document.querySelector("#algo_name"),
          placement: "right",
          showCloseButton: true
        },
        {
          title: "Manage strategies",
          content: "Click on the blue dots to edit, copy, delete your strategies.",
          target: document.querySelector(".menu_dots"),
          xOffset: 120,
          yOffset: -20,
          placement: "left",
          showPrevButton: true
        },
        {
          title: "Backtests",
          content: "Click to view backtest results.",
          target: document.querySelector(".menu_backtests"),
          xOffset: 120,
          yOffset: -20,
          placement: "left",
          showPrevButton: true
        },
        {
          title: "Search strategies",
          content: "Search strategies using strategy name, entry condition or instruments.",
          target: document.querySelector("#algos_search_input"),
          placement: "left",
          showPrevButton: true
        },
        {
          title: "Pagination",
          content: "Quickly navigate to a different page.",
          target: document.querySelector(".pagination"),
          placement: "right",
          showPrevButton: true
        }
      ]
    };
    return algos_tour;
 }