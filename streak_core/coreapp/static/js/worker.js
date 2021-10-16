console.log('inside service worker');
// importScripts('/static/js/jquery-2.1.4.min.js');
importScripts('https://cdnjs.cloudflare.com/ajax/libs/socket.io/2.0.3/socket.io.js');
// importScripts('/static/js/jquery.min.js');
importScripts('/static/js/ticker-v3.js?v=1.6');
importScripts('/static/js/cc-streamer.js?v=1.6');
var instrumentList = [];
var sym_segDict = {};
var sym_segList = [];
var crypto_exchanges = ['CCCAGG','Coinbase','GDAX','Binance','Bitfinex','OKEX','Huobi','HitBTC','Bithumb','BitBank','Poloniex'];
var crypto_exchanges_mapping = {'CCCAGG':'CCCAGG','COINBASE':'Coinbase','GDAX':'GDAX','BINANCE':'Binance','BITFINEX':'Bitfinex','OKEX':'OKEX','HUOBI':'Huobi','HITBTC':'HitBTC','BITHUMB':'Bithumb','BITBANK':'BitBank','POLONIEX':'Poloniex'};
var crypto_dict = {};
var crypto_list = [];
// var document = null;


crypto_exchanges = crypto_exchanges.join('|').toUpperCase().split('|');

function checkBrowser(){
    c = navigator.userAgent.search("Chrome");
    f = navigator.userAgent.search("Firefox");
    m8 = navigator.userAgent.search("MSIE 8.0");
    m9 = navigator.userAgent.search("MSIE 9.0");
    if (c > -1) {
        browser = "Chrome";
    } else if (f > -1) {
        browser = "Firefox";
    } else if (m9 > -1) {
        browser ="MSIE 9.0";
    } else if (m8 > -1) {
        browser ="MSIE 8.0";
    }
    return browser;
}
// document = ""

// require(['https://cdnjs.cloudflare.com/ajax/libs/socket.io/2.0.3/socket.io.slim.js'], function (io) {

	browser = checkBrowser();
    //foo is now loaded.
    domain = '0.0.0.0';
    // domain = 'notif.streak.tech';
	port = '8080';
	namespace = '/notification';
	// var socket = io('http://' + domain + ':' + port + namespace);

	domain = 'notif.streak.world';
	if(location.host=='127.0.0.1')
		domain = 'notif.streak.world';
	if(location.host.indexOf('ninja')==-1 && location.host!='127.0.0.1')
		domain = 'notif.streak.world';
	// var socket = io('https://' + domain + namespace);
	if(browser=='Firefox')
		var socket = io('https://' + domain + namespace,{transports: ['websocket'], upgrade: false});
	else
		var socket = io('https://' + domain + namespace);


	var crypto_current_price = {};
	var crypto_socket = io.connect('https://streamer.cryptocompare.com/');

	crypto_socket.on("m",function(message){
		crypto_tick(message);
	});

	function crypto_tick(message){
		// console.log(message);
		var messageType = message.substring(0, message.indexOf("~"));
		if (messageType == CCC.STATIC.TYPE.CURRENT||messageType == CCC.STATIC.TYPE.CURRENTAGG) {
			crypto_data_unpack(message);
		}
	}

	var crypto_data_unpack = function(message) {
		var data = CCC.CURRENT.unpack(message);

		var from = data['FROMSYMBOL'];
		var to = data['TOSYMBOL'];
		var market = data['MARKET']
		var fsym = CCC.STATIC.CURRENCY.getSymbol(from);
		var tsym = CCC.STATIC.CURRENCY.getSymbol(to);
		var pair = from + '/' + to + '_' + market;

		if (!crypto_current_price.hasOwnProperty(pair)) {
			crypto_current_price[pair] = {};
		}

		for (var key in data) {
			crypto_current_price[pair][key] = data[key];
		}

		if (crypto_current_price[pair]['LASTTRADEID']) {
			crypto_current_price[pair]['LASTTRADEID'] = parseInt(crypto_current_price[pair]['LASTTRADEID']).toFixed(0);
		}
		crypto_current_price[pair]['CHANGE24HOUR'] = CCC.convertValueToDisplay(tsym, (crypto_current_price[pair]['PRICE'] - crypto_current_price[pair]['OPEN24HOUR']));
		crypto_current_price[pair]['CHANGE24HOURPCT'] = ((crypto_current_price[pair]['PRICE'] - crypto_current_price[pair]['OPEN24HOUR']) / crypto_current_price[pair]['OPEN24HOUR'] * 100).toFixed(2) + "%";

		// console.log(crypto_current_price[pair]);
		postMessage({'notification-type':'crypto','ticks':[crypto_current_price[pair]],'sym_segDict':crypto_dict});
	};

	socket.on('disconnect', function() {
	    console.log('Disconnected');
	});
	socket.on('notification', function(msg) {
	    // console.log(msg.data);
	    postMessage(msg.data);
	});
	socket.on('connect', function() {
		// id = fetch_id();
		// if(id!=null)
	 //   		{
	 //   			socket.emit('user_acknowledgement', {auth: id});
	 	refresh_id();
	  	console.log('Connected');
	   	// 	}
	   	// else
	   	// 	{	
	   	// 		socket.disconnect();
	   	// 		console.log('Disconnected');
	   	// 	}
	});
	console.log('Here');

	// var ticker = new KiteTicker('xxx', 'AB0012', 
	// 	'xxxx');
	var ticker = new KiteTicker({
				api_key: "xxxx",
				access_token: "yyyyy"
			});
	//("wss://websocket.kite.trade/?api_key=xxx&user_id=AB0012&public_token=xxxx");

	ticker.connect();
	ticker.on("tick", setTick);
	ticker.on("ticks", setTick);// for kite-v3
	ticker.on("connect", subscribe);
	ticker.on("noreconnect", function() {
    	console.log("noreconnect");
	});
	ticker.on("reconnecting", function(reconnect_interval, reconnections) {
    	console.log("Reconnecting: attempet - ", reconnections, " innterval - ", reconnect_interval);
	});

	function setTick(ticks) {
	    // console.log("Ticks", ticks);
	    if(ticks instanceof Array)
		    if(ticks.length>0)
		    {
		    	if(ticks[0]['instrument_token']!=undefined) // this is present in kite-v3
		    	    postMessage({'notification-type':'ltp-v3','ticks':ticks,'sym_segDict':sym_segDict});
		    	else
					postMessage({'notification-type':'ltp','ticks':ticks,'sym_segDict':sym_segDict});
		    }

	}

	function subscribe() {
	    // var items = [738561];
	    // console.log(instrumentList);
	    // console.log('websocket Connected');
	    ticker.subscribe(instrumentList);
	    ticker.setMode(ticker.modeQuote, instrumentList);
	}
	function refresh_id(){
		var xhttp = new XMLHttpRequest();
	  	xhttp.open("GET", "/fetch_id/", true);
	  	xhttp.send();
	  	xhttp.onreadystatechange = function() {
	  		// console.log(xhttp.readyState);
			if (xhttp.readyState === 4 && xhttp.status === 200 && xhttp.responseText!='') {
				data = JSON.parse(xhttp.responseText);
				if(data['status']=='success'){
					socket.emit('user_acknowledgement', {auth: data['id']});
					// return data['id'];
				}
				else{
					return null;
				}
				return null;
			}
		};
	}

	onmessage = function(e) {
	  // console.log('Message received from main script');
	  // var workerResult = 'Result: ' + (e.data[0] * e.data[1]);
	  // console.log('Posting message back to main script');
	  // postMessage(workerResult);
	  var xhttp = new XMLHttpRequest();
	  if(e.data[0]=="subscribe" && e.data[1].includes('_') && !sym_segList.includes(e.data[1])){
		sym_segList.push(e.data[1]);

		var [seg,sym] = e.data[1].split(' ')[0].split('_')
		if(crypto_exchanges.indexOf(seg)<0)
			{
				params = {'seg_sym':e[1]};
				xhttp.open("GET", "/fetch_sym_tokens/?seg_sym="+e.data[1].replace('&','%26').replace(/_-_/g,'%20').replace(/ row_container/g,''), true);
				xhttp.send();
				// console.log('instrumentList')
				// console.log(instrumentList);
				xhttp.onreadystatechange = function() {
					// console.log(xhttp.readyState);
				if (xhttp.readyState === 4 && xhttp.status === 200 && xhttp.responseText!='') {
					data = JSON.parse(xhttp.responseText);
					if(data['status']=='success'){
						t = data['results'][0];
						if(!instrumentList.includes(t) || sym_segDict[t] == undefined){
							instrumentList.push(parseInt(t));
							sym_segDict[t]=e.data[1];
							subscribe();
							}
						}
					}
				};
			}
		else{
			if(crypto_dict[sym+'_'+seg]==undefined){
				crypto_dict[sym+'_'+seg]=seg;
				sub_id = '2'
				if(seg=='CCCAGG')
					sub_id = '5'
				crypto_list.push(sub_id+'~'+crypto_exchanges_mapping[seg]+'~'+sym.split('/')[0]+'~'+sym.split('/')[1]);
				crypto_socket.emit('SubAdd',{subs: crypto_list});
			}
		}
	  }
	  // if(e.data[0])
	}

	postMessage({'notification-type':'state','state':'ready'});
// });
// const io = require('https://cdnjs.cloudflare.com/ajax/libs/socket.io/1.3.5/socket.io.min.js');

// self.addEventListener('install', function(event) {
//   console.log("SW installed");
// });

// self.addEventListener('activate', function(event) {
//   console.log("SW activated");
//   document  = new Response("Hello world!");//);

// });

// self.addEventListener('fetch', function(event) {
//   console.log("Caught a fetch!");
  	
// });