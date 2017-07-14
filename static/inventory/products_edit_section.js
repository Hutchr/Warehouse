function activateNav() {
  $('ul.nav > li').on('click', function (evt) {
    if ($(evt.currentTarget).hasClass('toggle-nav')) return;
    $(evt.currentTarget).addClass('active').siblings().removeClass('active');
  });
}


var docs = [
  {
    "Type": "excel",
    "Name": "Remaining tasks for this app",
    "Description": "This is a list of all the remaining tasks required to complete this app",
    "Tags": "Responsive, RWD",
    "LastViewed": "an hour ago",
    "Expiration": "Sep 17, 2015"
  },
  {
    "Type": "ppt",
    "Name": "EVAMs presentation",
    "Description": "This is presentation for the EVAM occuring later this month",
    "Tags": "EVAM",
    "LastViewed": "a day ago",
    "Expiration": "Sep 08, 2015"
  },
  {
    "Type": "word",
    "Name": "Xmas Party list",
    "Description": "List of all the people who will be attending the holiday party",
    "Tags": "Responsive, RWD",
    "LastViewed": "a few mins ago",
    "Expiration": "Dec 25, 2014"
  }
];


function addToggle() {
	$('li.toggle-nav').on('click', function () {
		$(this).find('i').toggleClass('rotate-180-deg');
		$('.navbar-nav.side-nav').toggleClass('hide-link-text');
		$('#wrapper').toggleClass('expanded');
	});
}

function fixHamburgerUl() {
	$('.navbar-toggle').on('click', function () {
		$('.navbar-nav.side-nav').removeClass('hide-link-text');
		$("#wrapper").removeClass('expanded');
		$('i.fa-arrow-left').removeClass('rotate-180-deg');
	});
}

function init() {
  activateNav();
  addToggle();
  fixHamburgerUl();
}

init();