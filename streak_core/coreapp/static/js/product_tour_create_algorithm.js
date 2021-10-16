 $(document).ready(function(){
 // Define the tour!
    var tour = {
      id: "hello-hopscotch",
      steps: [
        {
          title: "Instruments",
          content: "Add upto 20 equities or future contracts.",
          target: document.querySelector("#equities_input"),
          placement: "left",
          showCloseButton: true
        },
        {
          title: "Candle interval",
          content: "Select minute, hour or day candle intervals.",
          target: document.querySelector("#ip_interval"),
          placement: "left",
          showPrevButton: true
        },
        {
          title: "Position",
          content: "Select a direction: buy/sell.",
          target: "ip_position_type",
          placement: "left",
          showPrevButton: true
        },
        {
          title: "Quantity",
          content: "Enter total number of shares for example: 40 for 1 lot of BANKNIFTY. For Currency Futures 1 is considered as 1 lot.",
          target: "ip_position_qty",
          placement: "left",
          showPrevButton: true
        },
        {
          title: "Indicator",
          content: "Select a technical indicator to form a condition.",
          target: document.querySelector("#display_condition1 div:first-child input"),
          placement: "top",
          showPrevButton: true
        },
        {
          title: "Comparator",
          content: "Select a comparator.",
          target: document.querySelector("#display_condition1 div:nth-child(2) input"),
          placement: "top",
          showPrevButton: true
        },
        {
          title: "Indicator",
          content: "Select a technical indicator or a number to compare against.",
          target: document.querySelector("#display_condition1 div:nth-child(3) input"),
          placement: "top",
          showPrevButton: true
        },
        {
          title: "Exit condition - Stop loss",
          content: "Enter a stop loss percentage.",
          target: "ip_stop_loss",
          placement: "top",
          showPrevButton: true
        },
        {
          title: "Exit condition - Target profit",
          content: "Enter a target profit percentage.",
          target: "ip_take_profit",
          placement: "top",
          showPrevButton: true
        },
        {
          title: "Strategy name",
          content: "Give your strategy a name.",
          target: "ip_strategy_name",
          placement: "top",
          showPrevButton: true
        },
        {
          title: "Advanced options",
          content: "Click here to edit chart type, order type and enter trade between time. Backtest is run keeping intraday orders (MIS) as default. You can change it to CNC/NRML from advanced section.",
          target: "advanced_section",
          placement: "top",
          showPrevButton: true
        },
        {
          title: "Backtest",
          content: "Save and backtest your strategy.",
          target: "algo_submit",
          placement: "top",
          showPrevButton: true
        }
      ]
    };
    if (first_time_create_algorithm == "true"){
      hopscotch.startTour(tour);
    }
    // if (go_sample_algo == "true"){
    //   hopscotch.startTour(go_algo_tour());
    // }
    $("#take_tour, #take_tour_mobile").click(function(){
      hopscotch.startTour(create_algo_tour());
    });
});
function create_algo_tour(){
  var create_algo_tour = {
      id: "hello-hopscotch",
      steps: [
        {
          title: "Instruments",
          content: "Add upto 20 equities or future contracts.",
          target: document.querySelector("#equities_input"),
          placement: "left",
          showCloseButton: true
        },
        {
          title: "Candle interval",
          content: "Select minute, hour or day candle intervals.",
          target: document.querySelector("#ip_interval"),
          placement: "left",
          showPrevButton: true
        },
        {
          title: "Position",
          content: "Select a direction: buy/sell.",
          target: "ip_position_type",
          placement: "left",
          showPrevButton: true
        },
        {
          title: "Quantity",
          content: "Enter total number of shares for example: 40 for 1 lot of BANKNIFTY. For Currency Futures 1 is considered as 1 lot.",
          target: "ip_position_qty",
          placement: "left",
          showPrevButton: true
        },
        {
          title: "Indicator",
          content: "Select a technical indicator to form a condition.",
          target: document.querySelector("#display_condition1 div:first-child input"),
          placement: "top",
          showPrevButton: true
        },
        {
          title: "Comparator",
          content: "Select a comparator.",
          target: document.querySelector("#display_condition1 div:nth-child(2) input"),
          placement: "top",
          showPrevButton: true
        },
        {
          title: "Indicator",
          content: "Select a technical indicator or a number to compare against.",
          target: document.querySelector("#display_condition1 div:nth-child(3) input"),
          placement: "top",
          showPrevButton: true
        },
        {
          title: "Exit condition - Stop loss",
          content: "Enter a stop loss percentage.",
          target: "ip_stop_loss",
          placement: "top",
          showPrevButton: true
        },
        {
          title: "Exit condition - Target profit",
          content: "Enter a target profit percentage.",
          target: "ip_take_profit",
          placement: "top",
          showPrevButton: true
        },
        {
          title: "Strategy name",
          content: "Give your strategy a name.",
          target: "ip_strategy_name",
          placement: "top",
          showPrevButton: true
        },
        {
          title: "Advanced options",
          content: "Click here to edit chart type, order type and enter trade between time. Backtest is run keeping intraday orders (MIS) as default. You can change it to CNC/NRML from advanced section.",
          target: "advanced_section",
          placement: "top",
          showPrevButton: true
        },
        {
          title: "Backtest",
          content: "Save and backtest your strategy.",
          target: "algo_submit",
          placement: "top",
          showPrevButton: true
        }
      ]
    };
    return create_algo_tour;
 }
 function go_algo_tour(){
  var go_algo_tour = {
      id: "go_algo_tour-hopscotch",
      steps: [
        // {
        //   title: "Instruments",
        //   content: "Add upto 5 equities or future contracts",
        //   target: document.querySelector("#equities_input"),
        //   placement: "left",
        //   showCloseButton: true
        // },
        {
          title: "Strategy name",
          content: "Give your strategy a name.",
          target: "ip_strategy_name",
          placement: "left",
          nextOnTargetClick: true,
          showCloseButton: true
        },
        {
          title: "Backtest",
          content: "Save and backtest your strategy.",
          target: "algo_submit",
          placement: "left",
          showPrevButton: true
        }
      ]
    };
    return go_algo_tour;
 }