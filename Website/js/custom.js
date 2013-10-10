//sliders autoplay
	//intro slider
	$('#carousel_fade_intro').carousel({
		interval: 2500,
		pause: "false"
	})

//make section height of window
	$(function(){
		$('#intro').css({'height':($(window).height())+'px'});
		$(window).resize(function(){
		$('#intro').css({'height':($(window).height())+'px'});
		});
	});



//smooth scroll on page
	$(function() {
		$('a').bind('click',function(event){
		var $anchor = $(this);

		$('[data-spy="scroll"]').each(function () {
		var $spy = $(this).scrollspy('refresh')
		});

		$('html, body').stop().animate({
		scrollTop: $($anchor.attr('href')).offset().top -61
		}, 1500,'easeInOutExpo');

		event.preventDefault();
		});
	});



//collapse menu on click on mobile and tablet devices
	$('.nav a').click(function () { $(".nav-collapse").collapse("hide") });