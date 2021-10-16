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
    if (first_time_dashboard == "true"){
      hopscotch.startTour(dashboard_tour());
    }
    $("#take_tour, #take_tour_mobile").click(function(){
      hopscotch.startTour(dashboard_tour());
    });
});
function dashboard_tour(){
  var dashboard_tour = {
      id: "hello-hopscotch",
      steps: [
        {
          title: "Funds",
          content: "Available balance, margins used and account value.",
          target: document.querySelector(".funding_subsection"),
          placement: "left",
          showCloseButton: true
        },
        {
          title: "Sample strategies",
          content: "Sample strategies to get you started. Copy or view strategy details to create your own.",
          target: "samples_table",
          placement: "top",
          xOffset: "center",
          showPrevButton: true
        },
        {
          title: "Top performers",
          content: "Your top 3 best performing strategies based on backtest results.",
          target: "top_performers_table",
          placement: "top",
          xOffset: "center",
          showPrevButton: true
        },
        {
          title: "Usage",
          content: "Snapshot of today's usage.",
          target: document.querySelector(".usage_header"),
          placement: "top",
          showPrevButton: true
        }
        // {
        //   title: "Edit algo",
        //   content: "You will be taken to the edit algo page.",
        //   target: document.querySelector("#icon-edit"),
        //   placement: "bottom",
        //   showPrevButton: true
        // },
        // {
        //   title: "Deploy",
        //   content: "Take your algo live in the market via Zerodha. Deploying will activate actionable alerts for entry and exit signals as per your algo.",
        //   target: document.querySelector("#deploy"),
        //   placement: "left",
        //   showPrevButton: true
        // },
        // {
        //   title: "Force stop",
        //   content: "This will stop your algo and you will not receive further alerts.",
        //   target: document.querySelector("#force_stop"),
        //   placement: "left",
        //   showPrevButton: true
        // },
        // {
        //   title: "Order tree",
        //   content: "Click here to see the tree of events that have occured since deploying your algo for this equity",
        //   target: "view_od",
        //   placement: "left",
        //   showPrevButton: true
        // }
      ]
    };
    return dashboard_tour;
 }