function addToFollow(productId) {
    fetch('/products/follow/' + productId + '/')
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('Error when adding an item to cart');
            }
        })
        .then(data => {
            if (data.success) {
                showNotification(data.product + ": " + data.message);
            } else {
                showNotification(data.message, success = false);
            }
        })
        .catch(error => {
            console.error(error);
            showNotification('Authorization required', success = false);
            window.location.href = '/user/login/';
        });
}

$(document).ready(function () {

    $("[data-fancybox='carousel-gallery']").fancybox({
        arrows: true,
        infobar: true,
        buttons: ["zoom", "slideShow", "fullScreen", "close"],
        protect: true,
        transitionEffect: "slide",
    });

    function bindAddToBasketEvent() {
        $('.add-to-basket').click(function (e) {
            e.preventDefault();
            var productId = $(this).data('product-id');
            addToBasket(productId);
        });
    }

    $(document).on('click', '.follow-product-availability', function (e) {
        e.preventDefault();
        var productId = $(this).data('product-id');
        addToFollow(productId);
    });

    function addToBasket(productId) {
        fetch('/products/basket/add/' + productId + '/')
            .then(response => {
                if (response.ok) {
                    return response.json();
                } else {
                    throw new Error('Error when adding an item to cart');
                }
            })
            .then(data => {
                if (data.success) {
                    showNotification(data.product_name + data.message);
                } else {
                    showNotification(data.message, success = false);
                }
            })
            .catch(error => {
                console.error(error);
                showNotification('Authorization required', success = false);
                window.location.href = '/user/login/'; // Перенаправляем пользователя на страницу входа
            });
    }


    function showNotification(message, success = true) {
        toastr.options = {
            "progressBar": true,
            "positionClass": "toast-bottom-left",
            "timeOut": "2000",
        }
        if (success) {
            toastr.success(message);
        } else {
            toastr.warning(message);
        }
    }

    bindAddToBasketEvent();
});
