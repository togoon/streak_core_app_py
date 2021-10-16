 $(document).ready(function(){
 // Define the tour!
    
    if (first_time_portfolio == "true"){
      hopscotch.startTour(portfolio_tour());
    }
    $("#take_tour, #take_tour_mobile").click(function(){
      hopscotch.startTour(portfolio_tour());
    });
});
 function portfolio_tour(){
 var portfolio_tour = {
      id: "hello-hopscotch",
      steps: [
        {
          title: "Positions",
          content: "Shows all your open positions.",
          target: "positions_option",
          placement: "bottom",
          nextOnTargetClick: true,
          showCloseButton: true
        },
        {
          title: "Holdings",
          content: "Shows all your holdings.",
          target: "holdings_option",
          placement: "bottom",
          nextOnTargetClick: true,
          showPrevButton: true
        },
        {
          title: "Choose Platform",
          content: "Click here to switch between trades taken only on Streak and all trades placed through Kite.",
          target: document.querySelector(".fancy_filter_select"),
          placement: "left",
          nextOnTargetClick: true,
          showPrevButton: true
        }
        // {
        //   title: "P&L",
        //   content: "Shows your unrealised/realised profit and the waiting stop loss and take profit prices. Once the price hits SL or TP you will get an actionable alert to buy/sell.",
        //   target: document.querySelector(".orders_details:first-child .new_pnl_div"),
        //   placement: "bottom",
        //   showPrevButton: true
        // },
        // {
        //   title: "Force stop",
        //   content: "This will stop your algo and you will not receive further alerts.",
        //   target: document.querySelector(".orders_details:first-child .force_stop"),
        //   placement: "left",
        //   showPrevButton: true
        // },
        // {
        //   title: "Order tree",
        //   content: "Click here to see the tree of events that have occured since deploying your algo for this equity.",
        //   target: document.querySelector(".orders_details:first-child .icon-order-log"),
        //   placement: "left",
        //   showPrevButton: true
        // }
      ]
    };
    return portfolio_tour;
 }