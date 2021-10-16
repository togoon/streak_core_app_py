 $(document).ready(function(){
 // Define the tour!
    var tour = {
      id: "hello-hopscotch",
      steps: [
        {
          title: "Edit parameters",
          content: "Click here to edit parameters such as backtest period, stop loss, target profit, chart type and more.",
          target: "open_parameters",
          placement: "left",
          showCloseButton: true
        },
        {
          title: "View strategy details",
          content: "Click here to view details of the strategy.",
          target: "view_algo_details",
          placement: "bottom",
          showPrevButton: true
        },
        {
          title: "Search strategies",
          content: "Search strategies using strategy name, entry condition or instruments to view their backtest results.",
          target: "algos_search_input",
          placement: "bottom",
          showPrevButton: true
        },
        {
          title: "Select all",
          content: "Select one or more instruments, to deploy.",
          target: "deploy_all_checkbox",
          yOffset: -20,
          xOffset: -15,
          placement: "left",
          showPrevButton: true
        },
        {
          title: "Deploy",
          content: "Take your strategy live in the market for all the selected instruments via Zerodha. Deploying will activate actionable alerts for entry and exit signals as per your strategy.",
          target: "deploy",
          placement: "left",
          showPrevButton: true
        },
        {
          title: "Backtest results",
          content: "Click here to see P&L curve and backtest performance metrics.",
          target: document.querySelector(".multiple_backtest_body"),
          placement: "top",
          showPrevButton: true
        },
        {
          title: "P&L curve",
          content: "A curve of running P&L for the duration of your backtest period. It shows hypothetical trades performed based on the entry and exit signals in your strategy.",
          target: document.querySelector(".multiple_backtest_row_second_wrapper"),
          placement: "top",
          showPrevButton: true
        },
        {
          title: "Hypothetical transaction details",
          content: "Click to view hypothetical trade details based on the entry and exit conditions in your strategy.",
          target: "transactions_section",
          placement: "top",
          yOffset: 7,
          xOffset: 10,
          showPrevButton: true
        },
        {
          title: "Performance metrics",
          content: "P&L, winning streak, number of trade signals generated and other backtest result metrics that measure the performance of your strategy.",
          target: "pnl_section",
          placement: "left",
          showPrevButton: true
        },
        {
          title: "Stock performance",
          content: "A measure of how the stock performed in the duration of the backtest period. This is independent of your strategy.",
          target: "fundamentals_section",
          placement: "left",
          showPrevButton: true
        },
        {
          title: "Download",
          content: "You can download the backtest trade results.",
          target: document.querySelector(".action_download_row_detail"),
          placement: "left",
          yOffset: -7,
          showPrevButton: true
        }
      ]
    };
    if (first_time_backtest == "true"){
      hopscotch.startTour(tour);
    }
    $("#take_tour, #take_tour_mobile").click(function(){
      hopscotch.startTour(backtest_tour());
    });
});
function backtest_tour(){
  var backtest_tour = {
      id: "hello-hopscotch",
      steps: [
        // {
        //   title: "Hypothetical capital for backtest",
        //   content: "Enter sufficient capital to run your backtest. Note: This is not the actual capital from your brokerage account, this is a hypothetical capital that is required to run a backtest.",
        //   target: "ip_initial_capital",
        //   placement: "bottom",
        //   showCloseButton: true
        // },
        // {
        //   title: "Quantity",
        //   content: "You can edit the total number of shares",
        //   target: "ip_quantity",
        //   placement: "bottom",
        //   showPrevButton: true
        // },
        // {
        //   title: "Stop Loss percentage",
        //   content: "You can edit the stop loss percentage that is a part of your exit condition in your algo.",
        //   target: "ip_stoploss",
        //   placement: "bottom",
        //   showPrevButton: true
        // },
        // {
        //   title: "Target Profit percentage",
        //   content: "You can edit the target profit percentage that is a part of your exit condition in your algo.",
        //   target: "ip_takeprofit",
        //   placement: "bottom",
        //   showPrevButton: true
        // },
        // {
        //   title: "Order type",
        //   content: "Select the order type for which you want to backtest. MIS orders will be squared off at the end of trading hours everyday, irrespective of SL and TP in your algo.",
        //   target: "ip_holding_type",
        //   placement: "bottom",
        //   showPrevButton: true
        // },
        // {
        //   title: "Candle Interval",
        //   content: "Select the candle interval for your algo. All technical indicators used as part of entry condition and the exit condition for the backtest will be calculated by taking the close price of the candle interval.",
        //   target: "ip_interval",
        //   placement: "bottom",
        //   showPrevButton: true
        // },
        // {
        //   title: "Backtesting period",
        //   content: "This is the time period for which your backtest will run.",
        //   target: "date_range",
        //   placement: "bottom",
        //   showPrevButton: true
        // },
        // {
        //   title: "Add equities",
        //   content: "You can add upto 20 equities or future contracts to backtest at once. You can also remove the added equities and add new ones.",
        //   target: "equities_input",
        //   placement: "bottom",
        //   showPrevButton: true
        // },
        // {
        //   title: "Re-run backtest",
        //   content: "After editing any of the backtest input parameters, click here to run a new backtest with all the changed parameters.",
        //   target: "run_backtest",
        //   placement: "left",
        //   showPrevButton: true
        // },
        // {
        //   title: "Edit algo",
        //   content: "Click here to edit your algo. You will be taken to the edit algo page.",
        //   target: "edit_strategy",
        //   placement: "left",
        //   showPrevButton: true
        // },
        // {
        //   title: "Select all",
        //   content: "Selects all the backtested instruments.",
        //   target: "deploy_all_checkbox",
        //   yOffset: -20,
        //   placement: "left",
        //   showPrevButton: true
        // },
        // {
        //   title: "Deploy",
        //   content: "Take your algo live in the market for all the selected instruments via Zerodha. Deploying will activate actionable alerts for entry and exit signals as per your algo.",
        //   target: "deploy",
        //   placement: "left",
        //   showPrevButton: true
        // },
        // {
        //   title: "Backtest results",
        //   content: "Click here to see P&L curve and backtest performance metrics",
        //   target: document.querySelector(".multiple_backtest_body"),
        //   placement: "top",
        //   showPrevButton: true
        // },
        // {
        //   title: "P&L curve",
        //   content: "A curve of running P&L for the duration of your backtest period. It shows hypothetical trades performed based on the entry and exit signals in your algo.",
        //   target: document.querySelector(".multiple_backtest_row_second_wrapper"),
        //   placement: "top",
        //   showPrevButton: true
        // },
        // {
        //   title: "Hypothetical transaction details",
        //   content: "Click to view hypothetical trade details based on the entry and exit conditions in your algo.",
        //   target: "transactions_section",
        //   placement: "top",
        //   showPrevButton: true
        // },
        // {
        //   title: "Performance metrics",
        //   content: "P&L, winning streak, number of trade signals generated and other backtest result metrics that measure the performance of your algo",
        //   target: "pnl_section",
        //   placement: "left",
        //   showPrevButton: true
        // },
        // {
        //   title: "Stock performance",
        //   content: "A measure of how the stock performed in the duration of the backtest period. This is independent of your algo.",
        //   target: "fundamentals_section",
        //   placement: "left",
        //   showPrevButton: true
        // },
        // {
        //   title: "Download",
        //   content: "You can download the backtest trade results or share the backtest results on social media",
        //   target: document.querySelector(".action_download_row_detail"),
        //   placement: "left",
        //   showPrevButton: true
        // }
        {
          title: "Edit parameters",
          content: "Click here to edit parameters such as backtest period, stop loss, target profit, chart type and more.",
          target: "open_parameters",
          placement: "left",
          showCloseButton: true
        },
        {
          title: "View strategy details",
          content: "Click here to view details of the strategy.",
          target: "view_algo_details",
          placement: "bottom",
          showPrevButton: true
        },
        {
          title: "Search strategies",
          content: "Search strategies using strategy name, entry condition or instruments to view their backtest results.",
          target: "algos_search_input",
          placement: "bottom",
          showPrevButton: true
        },
        {
          title: "Select all",
          content: "Select one or more instruments, to deploy.",
          target: "deploy_all_checkbox",
          yOffset: -20,
          xOffset: -15,
          placement: "left",
          showPrevButton: true
        },
        {
          title: "Deploy",
          content: "Take your strategy live in the market for all the selected instruments via Zerodha. Deploying will activate actionable alerts for entry and exit signals as per your strategy.",
          target: "deploy",
          placement: "left",
          showPrevButton: true
        },
        {
          title: "Backtest results",
          content: "Click here to see P&L curve and backtest performance metrics.",
          target: document.querySelector(".multiple_backtest_body"),
          placement: "top",
          showPrevButton: true
        },
        {
          title: "P&L curve",
          content: "A curve of running P&L for the duration of your backtest period. It shows hypothetical trades performed based on the entry and exit signals in your strategy.",
          target: document.querySelector(".multiple_backtest_row_second_wrapper"),
          placement: "top",
          showPrevButton: true
        },
        {
          title: "Hypothetical transaction details",
          content: "Click to view hypothetical trade details based on the entry and exit conditions in your strategy.",
          target: "transactions_section",
          placement: "top",
          yOffset: 7,
          xOffset: 10,
          showPrevButton: true
        },
        {
          title: "Performance metrics",
          content: "P&L, winning streak, number of trade signals generated and other backtest result metrics that measure the performance of your strategy.",
          target: "pnl_section",
          placement: "left",
          showPrevButton: true
        },
        {
          title: "Stock performance",
          content: "A measure of how the stock performed in the duration of the backtest period. This is independent of your strategy.",
          target: "fundamentals_section",
          placement: "left",
          showPrevButton: true
        },
        {
          title: "Download",
          content: "You can download the backtest trade results.",
          target: document.querySelector(".action_download_row_detail"),
          placement: "left",
          yOffset: -7,
          showPrevButton: true
        }
      ]
    };
    return backtest_tour;
 }