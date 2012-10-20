// ==UserScript==
// @name         The Next Reddit Helper
// @namespace    danneh_tnr
// @description  Helps The Next Reddit style
// @include      *.reddit.com/*
// @version      8
// @require      http://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js
// ==/UserScript==


// the new reddit style block, for dynamic styles
var style = document.createElement('style');
style.type = 'text/css';

var style_css = "";

function addGlobalStyle_direct(css) {
   style_css += "\n" + css;
}

function addGlobalStyle(name, css) {
   style_css += "\n";
   style_css += name + " {\n";
   style_css += "    " + css + "\n";
   style_css += "}";
}

function parseGlobalStyle() {
   var head;
   head = document.getElementsByTagName('head')[0];
   if (!head) { return; }
   head.appendChild(style);
}
function updateGlobalStyle() {
   style.innerHTML = "/* The Next Reddit css */" + style_css;
}

parseGlobalStyle();
updateGlobalStyle();

// the new reddit body class, for tnr-specific css hacks
$('body').addClass('tnr');

// auto my reddits horisontal offset
var rt = $('#header-img').offset().left + $('#header-img').outerWidth() + 20;
if (($('body').outerWidth() / 2) < rt) {
	rt = $('body').outerWidth() / 2;
}
$('#sr-header-area').offset({ left: rt }).css('left', rt + ' !important');

// auto my reddits vertical offset
var num = function (value) { /* jsizes */
	return parseInt(value, 10) || 0;
};
//var logo_ht = $('#header-img').offset().top + $('#header-img').outerHeight() - num($('#header-img').css("margin-bottom"));
var header_ht = $('#header-bottom-left').offset().top + $('#header-bottom-left').outerHeight() - num($('#header-bottom-left').css("padding-bottom"));
var this_ht = $('#sr-header-area').outerHeight() + $('.sr-list').outerHeight() - num($('.sr-list').css("padding-bottom")) - 1;
var ht = header_ht - this_ht;
$('#sr-header-area').offset({ top: ht }).css('top', ht + ' !important');

// fix misaligned arrow bar, when header is different height
var ht = $('#header-bottom-right').offset()['top'];
$('.tabmenu').offset({ top: ht }).css('top', ht + ' !important');

// fix content margin-padding
/*var ht = num($('.content').css("margin-top"))
var total_ht = ht + num($('.content').css("padding-top"));
if (ht != 0) {
	$('.content').css("margin-top", "0 !important");
	$('.content').css("padding-top", total_ht + " !important");
}*/

// List view
$('body').addClass('tnr-collapsed');

$('<div id="tnr_listview"><span>list view</span></div>').prependTo('#header');
$('<div id="tnr_collapsedview"><span>collapsed view</span></div>').prependTo('#sr-header-area');

$('body').prepend('<div id="header-bottom-left-background"></div>');
//$('#sr-more-link').after('<div id="tnr_collapsedview"><span>collapsed view</span></div>');
$('#tnr_listview').css('height', $('#header-bottom-left').outerHeight());
$('#tnr_listview span').css('margin-top', $('.sr-list').offset().top);

if (GM_getValue("listStyleActive", false)) {
	$('#tnr_listview').hide();
	listStyleActivate();
}

$(document).on('click', '#tnr_listview', function(event) {
	$('#tnr_listview').slideUp(250);
	$('#tnr_collapsedview').slideDown(250);

	$('#sr-header-area').slideUp(250);
	$('#sr-header-area .dropdown').slideUp(250);
	$('#sr-header-area .sr-list').slideUp(250);
	$('#tnr_listview').slideUp(250, function () {
		$('#header-bottom-left-background').animate({width: 163}, 250);
		$('#header-bottom-left').animate({'margin-left': 163}, 250);
		$('#header-bottom-left .tabmenu').animate({'margin-left': (163-8)}, 250);
		$('body > .content').animate({'margin-left': 163}, 250);
		//$('#header').animate({'background-color': '#ffffff'}, 250);
		$('.footer-parent').animate({'margin-left': 163}, 250, function () {
			listStyleActivate();

			$('#sr-header-area').slideDown(250);
			$('#sr-header-area .dropdown').slideDown(250);
			$('#sr-header-area .sr-list').slideDown(250);
		});
	});
});

$(document).on('click', '#tnr_collapsedview', function(event) {
	$('#tnr_collapsedview').slideUp(250);
	$('#tnr_listview').slideDown(250);

	$('#sr-header-area').slideUp(250);
	$('#sr-header-area .dropdown').slideUp(250);
	$('#sr-header-area .sr-list').slideUp(250);
	$('#tnr_collapsedview').slideUp(250, function () {
		$('#header-bottom-left-background').animate({width: 0}, 250);
		$('#header-bottom-left').animate({'margin-left': 0}, 250);
		$('#header-bottom-left .tabmenu').animate({'margin-left': 0}, 250);
		$('body > .content').animate({'margin-left': 0}, 250);
		//$('#header').animate({'background-color': '#ffffff'}, 250);
		$('.footer-parent').animate({'margin-left': 0}, 250, function () {
			listStyleDeactivate();

			$('#sr-header-area').slideDown(250);
			$('#sr-header-area .dropdown').slideDown(250);
			$('#sr-header-area .sr-list').slideDown(250);
			$('#tnr_listview').slideDown(250);
		});
	});
});

$(document).on('click', '.tnr-list .sr-list li', function () {
	window.location = $('a', this).attr('href');
});

function listStyleActivate() {
	GM_setValue("listStyleActive", true);

	$('body').removeClass('tnr-collapsed');
	$('body').addClass('tnr-list');

	//$('body').prepend($('.tabmenu'));
	//$('body').prepend($('#header-bottom-left'));
	$('body').prepend($('#sr-header-area'));

	if (style_css.indexOf(".tnr-list #tnr-list-generated") == -1) {
		addGlobalStyle(".tnr-list #tnr-list-generated", "/* this just makes sure we don't include css twice */");

		addGlobalStyle('.tnr-list #header-bottom-left-background', 'wisdth: ' + 163 + 'px;');
		//addGlobalStyle('.tnr-list #sr-header-area li a', 'max-width: ' + ($('#header-bottom-left').outerWidth() - 30) + 'px !important;');

		addGlobalStyle('.tnr-list #header-bottom-left-background', 'width: 163px;');

		addGlobalStyle(".tnr-list #sr-header-area li a", "max-width: " + (163-30) + "px;");
		addGlobalStyle(".tnr-list > .content, .tnr-list .footer-parent, .tnr-list #header-bottom-left", "margin-left: 163px !important;");
		addGlobalStyle(".tnr-list .tabmenu", "margin-left: " + (163-8) + "px !important;");

		addGlobalStyle_direct(".tnr-list #sr-header-area {");
		addGlobalStyle_direct("    top: 0px !important;");
		addGlobalStyle_direct("    width: 163px;");
		addGlobalStyle_direct("}");

		updateGlobalStyle();
	}

	/*$('#tnr_listview').slideUp(100);
	$('#tnr_collapsedview').slideDown(100);*/
}

function listStyleDeactivate() {
	GM_setValue("listStyleActive", false);

	$('body').addClass('tnr-collapsed');
	$('body').removeClass('tnr-list');

	$('#header-bottom-left').append($('.tabmenu'));
	$('#header-bottom-right').before($('#header-bottom-left'));
	$('#header-bottom-left').before($('#sr-header-area'));
	//$('#header-bottom-left-background').hide();

	/*$('#tnr_collapsedview').slideUp(100);
	$('#tnr_listview').slideDown(100);*/
}