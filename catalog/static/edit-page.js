(function() {
  var categories = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.whitespace,
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    prefetch: '/catalog'
  });

  categories.initialize();

  $('#category').typeahead({
    source: categories.ttAdapter()
  });
}());