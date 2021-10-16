/* eslint-env browser, serviceworker, es6 */

'use strict';

/* eslint-disable max-len */

const applicationServerPublicKey = 'BP4mnZPOaiBC4ejxcGL1yGb-tECt9_-y-sg6mYUGQjp3MKUZK3FEfjYfLtdibjQaZ0uOZHxHAbTPtDL0mq2emAU';
// const notification_audio = new Audio('/static/js/notification_audio.mp3');
/* eslint-enable max-len */

function urlB64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding)
    .replace(/\-/g, '+')
    .replace(/_/g, '/');

  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

self.addEventListener('activate', event => {
  event.waitUntil(clients.claim());
});
// self.addEventListener('install', (event) => self.skipWaiting());
// self.addEventListener('activate', () => self.clients.claim());
// self.onactivate=function(a){a.waitUntil(self.clients.claim())};

self.addEventListener('push', function(event) {
  console.log('[Service Worker] Push Received.');
  console.log(`[Service Worker] Push had this data: "${event.data.text()}"`);
  var payload = JSON.parse(event.data.text());
  var notif = payload['data'];
  if(notif!=undefined && notif!=null)
  {
    var title_str = '';
    var body = '';
    console.log(payload);
    if (notif['notification-type'] == "order-notification"){
        title_str = notif['algo_name'];
        body = notif.action_type+' '+notif.quantity+' shares of '+notif.symbol+' at '+parseFloat(notif.trigger_price).toFixed(2);
    }
    if(notif['price_trigger-notification']!=undefined){
      var tpsl_key=notif['price_trigger-notification'];
      var trigger_type = notif['type'];
      var trigger_price = notif['trigger_price'];

      var tpsl_array = tpsl_key.split(':');
      var userid = tpsl_array[0];
      var depid = tpsl_array[1];
      var token = tpsl_array[3];
      var algo_name = tpsl_array[8];
      var action_type = tpsl_array[9];
      var quantity = tpsl_array[10];
      var algo_uuid = tpsl_array[11];
      var product = tpsl_array[12];
      var symbol = tpsl_array[13];
      var segment = tpsl_array[14];

      title_str = algo_name;

      var notification_msg = action_type+' '+quantity+' shares of '+symbol+' at '+parseFloat(trigger_price).toFixed(2);

      body = notification_msg;
    }

    notif['notification-type']
    const title = title_str
    const options = {
      body: body,
      icon: '/static/imgs/new/logo.svg', 
      badge: '/static/imgs/new/logo.svg',
      vibrate: [500,110,500,110,450,110,200,110,170,40,450,110,200,110,170,40,500],
      tag:'',
      sound: "/static/js/notification_audio.mp3",
    };

    event.waitUntil(self.registration.showNotification(title, options));
  }
});

self.addEventListener('notificationclick', function(event) {
  console.log('[Service Worker] Notification click Received.');

  event.notification.close();

  // event.waitUntil(
  //   clients.openWindow('https://streak.ninja/order_log/#notif')
  // );

  // This looks to see if the current is already open and  
  // focuses if it is  
  // event.waitUntil(
  //   clients.matchAll({  
  //     type: "window"  
  //   })
  //   .then(function(clientList) {  
  //     for (var i = 0; i < clientList.length; i++) {  
  //       var client = clientList[i];  
  //       if (client.url == '/' && 'focus' in client)  
  //         return client.focus();  
  //     }  
  //     if (clients.openWindow) {
  //       return clients.openWindow('https://streak.ninja/order_log/#notif');  
  //     }
  //   })
  // );
    const urlToOpen = new URL('order_log/', self.location.origin).href;

    const promiseChain = clients.matchAll({
      type: 'window',
      includeUncontrolled: true
    })
    .then((windowClients) => {
      let matchingClient = null;

      for (let i = 0; i < windowClients.length; i++) {
        const windowClient = windowClients[i];
        if (windowClient.url.indexOf('/order_log')>-1) {
          matchingClient = windowClient;
          break;
        }
      }

      if (matchingClient) {
        return matchingClient.focus();
      } else {
        return clients.openWindow(urlToOpen);
      }
    });

    event.waitUntil(promiseChain);

});

self.addEventListener('pushsubscriptionchange', function(event) {
  console.log('[Service Worker]: \'pushsubscriptionchange\' event fired.');
  const applicationServerKey = urlB64ToUint8Array(applicationServerPublicKey);
  event.waitUntil(
    self.registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: applicationServerKey
    })
    .then(function(newSubscription) {
      // TODO: Send to application server
      console.log('[Service Worker] New subscription: ', newSubscription);
    })
  );
});