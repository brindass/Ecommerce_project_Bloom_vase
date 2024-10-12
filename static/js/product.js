// product.js
$(document).ready(function(){
    $('.product__details__pic__slider').owlCarousel({
        items: 4,
        margin: 10,
        nav: true,
        dots: true,
        responsive: {
            0: {
                items: 2
            },
            600: {
                items: 3
            },
            1000: {
                items: 4
            }
        }
    });
});
