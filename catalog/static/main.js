window.UCatalog = window.UCatalog || {};

/**
 * Google and facebook Oauth providers
 */
(function() {

  function oauthConnect(provider, token) {
    $.ajax({
      type: 'POST',
      url: '/oauth-connect/'+provider, // TODO: CSRF
      processData: false,
      data: JSON.stringify({ token: token }),
      contentType: "application/json; charset=utf-8",
      success: function(result, statusText, xhr) {
        if (parseInt(xhr.status / 100) === 2) {
          window.location.href = "/";
        } else {
          console.error(statusText);
          $("#result").html(
            "Failed to make a server-side call. Check your configuration and console."
          );
        }
      },
      error: function(err) {
        console.log(err);
        $("#result").html(
          "Failed to make a server-side call. Check your configuration and console."
        );
      }
    });
  };

  gapi.load('auth2', function() {
    var auth2 = gapi.auth2.init({
      scope: 'openid email',
      client_id: '784559703256-93th4q9e73n3rdi1lr66m0u6fp6i9tqq.apps.googleusercontent.com'
    });

    $('.btn-social.btn-google').click(function() {
      auth2.grantOfflineAccess().then(googleSignInCallback);
    });
  });

  function googleSignInCallback(authResult) {
    if (authResult['code']) {
      oauthConnect('Google', authResult['code'])
    } else {
      // TODO: not logged in
    }
  }

  window.fbAsyncInit = function() {
    FB.init({
      appId: "291400941303173",
      cookie: true,
      xfbml: true,
      version: "v2.9"
    });
  };

  // Load the SDK asynchronously
  (function(d, s, id) {
    var js, fjs = d.getElementsByTagName(s)[0];
    if (d.getElementById(id)) return;
    js = d.createElement(s);
    js.id = id;
    js.src = "//connect.facebook.net/en_US/sdk.js";
    fjs.parentNode.insertBefore(js, fjs);
  })(document, "script", "facebook-jssdk");


  $('.btn-social.btn-facebook').click(function() {
    FB.login(function(response) {
      if (response.status === 'connected') {
        var accessToken = response.authResponse.accessToken;
        oauthConnect('Facebook', accessToken)
      } else {
        // TODO: not logged in
      }
    }, {scope: 'public_profile,email'});
  });
})();

