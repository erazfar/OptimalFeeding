$(document).ready(function(){
	var top = $(".top"),
		nav = $(".nav"),
		logo = $(".logo"),
		headerHeight = $('header').height(),

		aboutHeight = $(".about").height();
		aboutOffset = $(".about").offset().top,
		galleryHeight = $(".gallery").height();
		galleryOffset = $(".carousel").offset().top;
		contactHeight = $(".contact").height();
		contactOffset = $(".contact").offset().top;

		about = $(".nav-about"),
		gallery = $(".nav-gallery"),
		contact = $(".nav-contact");
// Sticky/resizeable Navbar
	$(window).scroll(function() {
		if($(window).scrollTop() > aboutOffset) {
			top.addClass("top-scroll");
			top.addClass("top-resized");
			nav.addClass("nav-resized");
			logo.addClass("logo-resized");
		}
		else {
			top.removeClass("top-scroll");
			top.removeClass("top-resized");
			nav.removeClass("nav-resized");
			logo.removeClass("logo-resized");
		} 
//Position Indicator
		if ($(window).scrollTop() < headerHeight) {
			about.removeClass("active");
		}
		//ABOUT
		else if ($(window).scrollTop() > aboutOffset && 
			($(window).scrollTop() < galleryOffset)) {
			gallery.removeClass("active");
			about.addClass("active");
		}	
		//GALLERY
		else if (($(window).scrollTop() > galleryOffset) && 
				($(window).scrollTop() < contactOffset)) {
			about.removeClass("active");
			gallery.addClass("active");
			contact.removeClass("active");
		}
		//CONTACT
		else if ($(window).scrollTop() > contactOffset) {
			gallery.removeClass("active");
			contact.addClass("active");
		}

	});
//Carousel
	var img1 = $("#img1"),
		img2 = $("#img2"),
		img3 = $("#img3");

	$("#right").click(function() {
		if (img1.is(":visible")) {
			img1.fadeOut(500);
			img2.fadeIn(500);
		}

		else if (img2.is(":visible")) {
			img2.fadeOut(500);
			img3.fadeIn(500);
		}

		else if (img3.is(":visible")) {
			img3.fadeOut(500);
			img1.fadeIn(500);
		}
	});

	$("#left").click(function() {
		if (img1.is(":visible")) {
			img1.fadeOut(500);
			img3.fadeIn(500);
		} 

		else if (img3.is(":visible")) {
			img3.fadeOut(500);
			img2.fadeIn(500);
		}

		else if (img2.is(":visible")) {
			img2.fadeOut(500);
			img1.fadeIn(500);
		}
	});
//Modal
	var layover = $(".layover");

	$(".button").click(function() {
		layover.toggle();
	});

	$(".layover").click(function() {
		layover.toggle();
	});
//Smooth scrolling
	$(".nav-about").click(function() {
		$('html, body').animate({
		    scrollTop: aboutOffset + 10
		}, 750);
	});

	$(".nav-gallery").click(function() {
		$('html, body').animate({
		    scrollTop: galleryOffset + 10
		}, 750);
	});

	$(".nav-contact").click(function() {
		$('html, body').animate({
		    scrollTop: contactOffset + 10
		}, 750);
	});
});