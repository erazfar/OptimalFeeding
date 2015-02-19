var divs = document.getElementsByTagName('div');
for(var i=0; i<divs.length; i++) {
	divs[i].addEventListener("click", highlightThis);
	/*
	divs[i].addEventListener("click", highlightThis, true);
	divs[i].addEventListener("click", highlightThis, false);*/
}
$(function(){
		$(".navbar").load("navbar.html"); 
});
$(document).ready(function(){
	// Set the interval to be 5 seconds
	var t = setInterval(function(){
		$("#carousel ul").animate({marginLeft:-1000},1000,function(){
			$(this).find("li:last").after($(this).find("li:first"));
			$(this).css({marginLeft:0});
		})
	},5000);
});

buttonWorker();

var stickyNav = function () {
		var scrollTop = $(window).scrollTop();
		var height = $(document).height();
		if (scrollTop >= 0) {
			$(".sticky-nav").slideDown();
		}
		else {
			$(".sticky-nav").slideUp();
		}
		if (scrollTop > 10) {
			$(".sticky-nav").addClass("shrink");
		}
		else {
			$(".sticky-nav").removeClass("shrink");
		}
		if (scrollTop == 0) {
		}
		else if (scrollTop + $(window).height() + 120 > height){
			$(".contact").addClass("scrollSelect");
			$(".about").removeClass("scrollSelect");
		}
		else if (height/2 - 80 < scrollTop) {
			$(".about").addClass("scrollSelect");
			$(".portfolio").removeClass("scrollSelect");
			$(".contact").removeClass("scrollSelect");
		}
		else if (height* (1/4) - 80 < scrollTop) {
			$(".portfolio").addClass("scrollSelect");
			$(".home").removeClass("scrollSelect");
			$(".about").removeClass("scrollSelect");
		}
		else {
			$(".home").addClass("scrollSelect");
			$(".portfolio").removeClass("scrollSelect");
		}
		
	};

	$(window).scroll(function () {
			stickyNav();
	});

function highlightThis(event) {
	
		var backgroundColor = this.style.backgroundColor;
		this.style.backgroundColor='yellow';
		alert(this.className);
		this.style.backgroundColor=backgroundColor;
}

function buttonWorker(type) {
	var divPosid = $("#"+type+"");
    if (!divPosid.length) {
        return;
    }
	$('html,body').animate({
	   scrollTop: $("#"+type+"").offset().top - 70
	});
}

function scrollPic() {
	console.log("YOOO");
	$("#carousel ul").animate({marginLeft:-1000},1,function(){
		$(this).find("li:last").after($(this).find("li:first"));
		$(this).css({marginLeft:0});
	})
}