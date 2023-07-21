// Initialize Fancybox for carousel images
    $(document).ready(function () {
        $("[data-fancybox='carousel-gallery']").fancybox({
            arrows: true,
            infobar: true,
            buttons: ["zoom", "slideShow", "fullScreen", "close"],
            protect: true,
            transitionEffect: "slide",
        });
    });