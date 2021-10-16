/*
*
*  Push Notifications codelab
*  Copyright 2015 Google Inc. All rights reserved.
*
*  Licensed under the Apache License, Version 2.0 (the "License");
*  you may not use this file except in compliance with the License.
*  You may obtain a copy of the License at
*
*      https://www.apache.org/licenses/LICENSE-2.0
*
*  Unless required by applicable law or agreed to in writing, software
*  distributed under the License is distributed on an "AS IS" BASIS,
*  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
*  See the License for the specific language governing permissions and
*  limitations under the License
*
*/

/* eslint-env browser, es6 */

'use strict';

const applicationServerPublicKey = 'BP4mnZPOaiBC4ejxcGL1yGb-tECt9_-y-sg6mYUGQjp3MKUZK3FEfjYfLtdibjQaZ0uOZHxHAbTPtDL0mq2emAU';
// const pushButton = document.querySelector('.js-push-btn');

let isSubscribed = false;
let swRegistration = null;

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

function refresh_subscription_id(subscription_str){
    var xhttp = new XMLHttpRequest();
    xhttp.open("GET", "/fetch_id/", true);
    xhttp.send();
    xhttp.onreadystatechange = function() {
      // console.log(xhttp.readyState);
    if (xhttp.readyState === 4 && xhttp.status === 200 && xhttp.responseText!='') {
      var data = JSON.parse(xhttp.responseText);
      if(data['status']=='success'){
        if(data['id']!=null)
        {
          $.ajax({
          "async": true,
          "crossDomain": true,
          "headers": {
            },
          type: "POST",
          // url: "https://notif."+"streak.ninja"+"/update_web_push_subscription/",
          url: "/update_web_push_subscription/",
          // url: "http://127.0.0.1:8080"+"/update_web_push_subscription/",
          data: {
                'subscription_str':subscription_str,
                'id':data['id']
            },
          success: function (data) {
              // do something with server response data
              console.log('updated subscription')  
            },
          error: function (err) {
              // handle your error logic here
            }
          });
        }
      }
      else{
        return null;
      }
      return null;
    }
  };
}

function updateBtn() {
  if (Notification.permission === 'denied') {
    // pushButton.textContent = 'Push Messaging Blocked.';
    // pushButton.disabled = true;
    // updateSubscriptionOnServer(null);
    return;
  }

  if (isSubscribed) {
    // pushButton.textContent = 'Disable Push Messaging';
  } else {
    // pushButton.textContent = 'Enable Push Messaging';
  }

  // pushButton.disabled = false;
}

function updateSubscriptionOnServer(subscription) {
  // TODO: Send subscription to application server
  if (subscription) {
    var subscription_str = JSON.stringify(subscription);
    // sending a post request 
    refresh_subscription_id(subscription_str);
    // subscriptionDetails.classList.remove('is-invisible');
  } else {
    // subscriptionDetails.classList.add('is-invisible');
  }
}

function subscribeUser() {
  try{
    const applicationServerKey = urlB64ToUint8Array(applicationServerPublicKey);
    swRegistration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: applicationServerKey
    })
    .then(function(subscription) {
      console.log('User is subscribed.');

      updateSubscriptionOnServer(subscription);

      isSubscribed = true;

      updateBtn();
    })
    .catch(function(err) {
      console.log('Failed to subscribe the user: ', err);
      updateBtn();
    });
  }catch(e){
    
  }
}

function unsubscribeUser() {
  swRegistration.pushManager.getSubscription()
  .then(function(subscription) {
    if (subscription) {
      return subscription.unsubscribe();
    }
  })
  .catch(function(error) {
    console.log('Error unsubscribing', error);
  })
  .then(function() {
    updateSubscriptionOnServer(null);

    console.log('User is unsubscribed.');
    isSubscribed = false;

    updateBtn();
  });
}

function initializeUI() {
  // pushButton.addEventListener('click', function() {
  //   pushButton.disabled = true;
  //   if (isSubscribed) {
  //     unsubscribeUser();
  //   } else {
      subscribeUser();
  //   }
  // });

  // Set the initial subscription value
  try{
    swRegistration.pushManager.getSubscription()
  .then(function(subscription) {
    isSubscribed = !(subscription === null);

    updateSubscriptionOnServer(subscription);

    if (isSubscribed) {
      console.log('User IS subscribed.');
    } else {
      console.log('User is NOT subscribed.');
    }

    updateBtn();
    });
  }catch(e){
    console.log('Cannot read property pushManager of null');
  }
}

if ('serviceWorker' in navigator && 'PushManager' in window) {
  console.log('Service Worker and Push is supported');

  navigator.serviceWorker.register('/static/js/sw.js?v=2.1',{ scope: '/static/js/' })
  .then(function(swReg) {
    console.log('Service Worker is registered', swReg);

    swRegistration = swReg;
    try{
    if(typeof user_is_auth !== "undefined")
      if(user_is_auth=="True")
        initializeUI();
    }
    catch(e){
      console.log(e);      
    }
  })
  .catch(function(error) {
    console.error('Service Worker Error', error);
  });
} else {
  console.warn('Push messaging is not supported');
  // pushButton.textContent = 'Push Not Supported';
}