$(document).ready(function(){
    // facebook init
    window.fbAsyncInit = function() {
    FB.init({
      appId            : '427759817640419',
      autoLogAppEvents : true,
      xfbml            : true,
      version          : 'v2.11'
    });
    };

    (function(d, s, id){
     var js, fjs = d.getElementsByTagName(s)[0];
     if (d.getElementById(id)) {return;}
     js = d.createElement(s); js.id = id;
     js.src = "https://connect.facebook.net/en_US/sdk.js";
     fjs.parentNode.insertBefore(js, fjs);
    }(document, 'script', 'facebook-jssdk'));

    // twitter init
    window.twttr = (function(d, s, id) {
      var js, fjs = d.getElementsByTagName(s)[0],
        t = window.twttr || {};
      if (d.getElementById(id)) return t;
      js = d.createElement(s);
      js.id = id;
      js.src = "https://platform.twitter.com/widgets.js";
      fjs.parentNode.insertBefore(js, fjs);

      t._e = [];
      t.ready = function(f) {
        t._e.push(f);
      };

      return t;
    }(document, "script", "twitter-wjs"));

    // linkedin init
    // el = document.createElement("script")
    // el.setAttribute("src", "//platform.linkedin.com/in.js")
    // el.innerHTML = "api_key: 812phsl9so3gi4\r\n" +                                                                      
    //               "onLoad: onLinkedInLoad\r\n" +                                                                      
    //               "authorize: true\r\n"
    // document.head.appendChild(el);
});

function share_to_facebook(url, tag){
    ga('send', {hitType: 'event', eventCategory: 'Share on FB', eventAction: 'Share on FB', eventLabel: 'Backtest page'});
    FB.ui({
    method: 'share',
    quote:'Algo trade, without coding',
    display: 'popup',
    href: url,
    hashtag: "#" + tag
    }, function(response){});
};

function share_to_twitter(url, tag){
    ga('send', {hitType: 'event', eventCategory: 'Share on Twitter', eventAction: 'Share on Twitter', eventLabel: 'Backtest page'});
    window.open("https://twitter.com/intent/tweet?url=" + url + "&hashtags=" + tag, 'name', 'height=500,width=500')
};

function onLinkedInLoad() {
  // IN.Event.on(IN, "auth", shareContent);
}

function share_to_linkedin(url, tag) {
    ga('send', {hitType: 'event', eventCategory: 'Share on LinkedIn', eventAction: 'Share on LinkedIn', eventLabel: 'Backtest page'});
    // var payload = { 
    //   "comment": url + "    #" + tag, 
    //   "visibility": { 
    //     "code": "anyone"
    //   } 
    // };

    // IN.API.Raw("/people/~/shares?format=json")
    //   .method("POST")
    //   .body(JSON.stringify(payload))
    //   // .result(onSuccess)
    //   // .error(onError);
    var title = tag;//"Replace this with a title.";
    var description = "Algo trade, without coding"
    var text = '#'+tag;//"Replace this with your share copy.";
    window.open('http://www.linkedin.com/shareArticle?mini=true&url='+encodeURIComponent(url)+'&title='+encodeURIComponent(title)+'&description='+encodeURIComponent(description)+'&text='+encodeURIComponent(text), '', 'left=0,top=0,width=650,height=420,personalbar=0,toolbar=0,scrollbars=0,resizable=0');
  }