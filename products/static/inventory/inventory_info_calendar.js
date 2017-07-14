$("li").click(function(e) {
  e.preventDefault();
  $("li").removeClass("selected");
  $(this).addClass("selected");
});