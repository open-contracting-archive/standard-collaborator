(function($){

    $("header .genesis-nav-menu").before('<div id="responsive-menu-icon" class="oi oi-menu"></div>');
    
    $("#responsive-menu-icon").click(function(){
        $("header .genesis-nav-menu").slideToggle();
    });
    
    $(window).resize(function(){
        if(window.innerWidth > 768) {
            $("header .genesis-nav-menu").removeAttr("style");
        }
    });
    
})($);
