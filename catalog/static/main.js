window.UCatalog = window.UCatalog || {};

if (!window.CURRENT_USER) {
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
}


(function() {

  var selectedClass = 'category-card__selected';
  function setSelectedState(state, card) {
    var method = state ? 'addClass' : 'removeClass';
    $(card)[method](selectedClass);
  }

  var fetchItemsFor = (function () {
    var __cache__ = {};
    return function innerFetchItemsFor(category) {
      if (__cache__[category]) {
        return Promise.resolve(__cache__[category]);
      }

      return new Promise(function(resolve, reject) {
        $.ajax({
          type: 'GET',
          url: '/'+category+'/items',
          dataType: 'json',
          success: function(items) {
            __cache__[category] = items;
            resolve(items);
          },
          error: reject
        });
      });
    };
  }());

  function showItemsFor(category, lastSelected) {
    fetchItemsFor(category).then(function(items) {
      var ul = $('<ul>');
      var title = $('<h2>');
      title.html(category);
      var fragment = $(document.createDocumentFragment());
      items.forEach(function(item) {
        var li = $('<li>');
        var href = '/items/'+item.id+'/show';
        li.html('<a href="'+href+'">'+item.title+'</a>');
        ul.append(li);
      });

      fragment.append(title);
      fragment.append(ul);
      var selectedCategoryItems = $('#selected-category-items');
      if (lastSelected) {
        selectedCategoryItems.fadeOut(200, function() {
          selectedCategoryItems.empty().append(fragment);
          selectedCategoryItems.fadeIn(200);
        });
      } else {
        var latestItems = $('#latest-items');
        latestItems.fadeOut(200, function() {
          selectedCategoryItems.empty().append(fragment);
          selectedCategoryItems.fadeIn(200);
        });
      }
    });
  }

  var allCategories = $('.category-card');
  var lastSelected = null;
  allCategories.each(function() {
    $(this).on('click', function() {
      var elem = $(this);
      var category = elem.data('category');
      if (elem.hasClass(selectedClass)) {
        setSelectedState(false, this);
        lastSelected = null;
        $('#selected-category-items').fadeOut(200, function() {
          $('#latest-items').fadeIn(200);
        });
      } else {
        allCategories.each(function() {
          setSelectedState(false, this);
        });
        setSelectedState(true, this);
        showItemsFor(category, lastSelected);
        lastSelected = category;
      }
    });
  })

}())
