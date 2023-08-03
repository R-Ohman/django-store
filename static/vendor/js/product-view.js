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

function deleteComment(commentId) {
    const currentPage = $('.pagination').find('.active > a').data('page'); // Получаем текущую активную страницу
    const url = '/products/comments/delete/' + commentId + '/?page=' + currentPage; // Добавляем параметр page к URL
    fetch(url)
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('Error when deleting comment');
            }
        })
        .then(data => {
            if (data.success) {
                showNotification(data.message);
                $('#comments').html(data.comments_html);
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

function addToWishlist(productId) {
    fetch('/user/wishlist/add/' + productId + '/')
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('Error when adding an item to cart');
            }
        })
        .then(data => {
            showNotification(data.message, data.success);
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

    $(document).on('click', '.delete-comment', function (e) {
        e.preventDefault();
        var commentId = $(this).data('comment-id');
        deleteComment(commentId);
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

    $(document).on('click', '.add-to-wishlist', function (e) {
        e.preventDefault();
        var productId = $(this).data('product-id');
        addToWishlist(productId);
    });

    bindAddToBasketEvent();
});
