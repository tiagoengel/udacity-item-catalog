(function() {
  function googleSignInCallback(authResult) {
    if (authResult["code"]) {
      // Send the one-time-use code to the server, if the server responds, write a 'login successful' message to the web page and then redirect back to the main restaurants page
      $.ajax({
        type: "POST",
        url: "/oauth-connect/Google", // TODO: CSRF
        processData: false,
        data: JSON.stringify({ token: authResult["code"] }),
        contentType: "application/json; charset=utf-8",
        success: function(result, status, xhr) {
          window.location.href = "/";
        },
        error: function(err) {
          console.log(err);
          $("#result").html(
            "Failed to make a server-side call. Check your configuration and console."
          );
        }
      });
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

  function facebookSignInCallback() {
    var access_token = FB.getAuthResponse()["accessToken"];
    console.log(access_token);
    console.log("Welcome!  Fetching your information.... ");
    FB.api("/me", function(response) {
      console.log("Successful login for: " + response.name);
      $.ajax({
        type: "POST",
        url: "/oauth-connect/Facebook", // TODO: CSRF
        processData: false,
        data: JSON.stringify({ token: access_token }),
        contentType: "application/json; charset=utf-8",
        success: function(result) {
          window.location.href = "/";
        },
        error: function(err) {
          console.log(err);
          $("#result").html(
            "Failed to make a server-side call. Check your configuration and console."
          );
        }
      });
    });
  }

  window.googleSignInCallback = googleSignInCallback;

  window.Oauth = {
    Google: { callback: googleSignInCallback },
    Facebook: { callback: facebookSignInCallback }
  }

  $('.modal').modal('show');
})();
