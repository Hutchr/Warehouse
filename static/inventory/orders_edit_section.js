$(".toggleNav").click(function () {
    $("#subnav").toggleClass("active");
    $(".toggleNavButton").toggleClass("active");
 });

$(function() {
    var availableTags = [

    ];
    $( "#tags" ).autocomplete({
      source: availableTags
    });
  });

