(function() {
  var categories = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.whitespace,
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    prefetch: '/catalog/categories.json'
  });

  categories.initialize();

  $('#category').typeahead({
    source: categories.ttAdapter()
  });
}());