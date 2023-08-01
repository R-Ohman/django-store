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
            var basket = document.querySelector('#basket-list');
            basket.innerHTML = data.basket_list_html;

            showNotification(data.message, data.success);
        })
        .catch(error => {
            console.error(error);
            showNotification('Authorization required', success = false);
            window.location.href = '/user/login/';
        });
}

function bindAddToBasketEvent() {
    $('.add-to-basket').click(function (e) {
        e.preventDefault();
        var productId = $(this).data('product-id');
        addToBasket(productId);
        addListenersToInputs();
    });
}

function addListenersToInputs() {
    const fileInput = document.querySelector('.custom-file-input');
    const label = document.querySelector('.custom-file-label');

    fileInput.addEventListener('change', (event) => {
        const fileName = event.target.files[0].name;
        label.textContent = fileName;
    });


    const quantityInputs = document.querySelectorAll('.basket-quantity');
    quantityInputs.forEach((input) => {
        input.addEventListener('change', (event) => {
            const quantity = event.target.value;
            const basketId = parseInt(event.target.dataset.basketId, 10);
            const inputElement = event.target; // Сохраняем ссылку на входной элемент
            const csrfToken = document.querySelector('[data-csrf-token]').dataset.csrfToken; // Получаем CSRF-токен

            fetch(`/products/basket/update/${basketId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken // Используем полученный CSRF-токен
                },
                body: JSON.stringify({quantity: quantity})
            })
                .then(response => response.json())
                .then(data => {
                    // Обновить информацию на странице
                    const totalQuantityElement = document.querySelector('.total_quantity');
                    const totalSumElement = document.querySelector('.total_sum');
                    const productSumWithoutDiscountElement = document.querySelector('#product-' + basketId);
                    const productSumElement = document.querySelector('#product-discount-' + basketId);

                    if (totalQuantityElement && totalSumElement && productSumWithoutDiscountElement) {
                        totalQuantityElement.textContent = data.total_quantity.toLocaleString('en-EN');
                        totalSumElement.textContent = data.total_sum.toLocaleString('en-EN', {minimumFractionDigits: 2});
                        if (productSumElement) {
                            productSumElement.textContent = data.product_sum.toLocaleString('en-EN', {minimumFractionDigits: 2});
                        }
                        productSumWithoutDiscountElement.textContent = data.product_sum_without_discount.toLocaleString('en-EN', {minimumFractionDigits: 2});
                        event.target.value = data.quantity;
                    }
                })
                .catch(error => {
                    console.error('Error when updating the quantity in the cart: ', error);
                    inputElement.value = inputElement.defaultValue; // Используем сохраненную ссылку для изменения значения
                });
        });
    });
}

function unfollowProduct(productId) {
    var csrfToken = document.querySelector('[data-csrf-token]').dataset.csrfToken;
    fetch('/products/unfollow/' + productId + '/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                $('#product-following-' + productId).remove();
                showNotification(data.message, data.success);
            } else {
                console.error('Error when unfollowing product');
            }
        })
        .catch(error => {
            console.error('Error when unfollowing product:', error);
        });
}

function deleteFromWishlist(productId) {
    var csrfToken = document.querySelector('[data-csrf-token]').dataset.csrfToken;
    fetch('/user/wishlist/delete/' + productId + '/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                $('#product-wishlist-' + productId).remove();
            } else {
                console.error('Error when deleting an item from the wishlist');
            }
        })
        .catch(error => {
            console.error('Error when deleting an item from the wishlist:', error);
        });
}

$(document).ready(function () {
    document.addEventListener('DOMContentLoaded', addListenersToInputs);

    bindAddToBasketEvent();
});

$(document).on('click', '.delete-basket', function (e) {
    e.preventDefault();
    var basketId = $(this).data('basket-id');
    deleteBasket(basketId);
});

$(document).on('click', '.clear-baskets', function (e) {
    e.preventDefault();
    $('.delete-basket').each(function () {
        var basketId = $(this).data('basket-id');
        deleteBasket(basketId);
    });
});

$(document).on('click', '.delete-from-wishlist', function (e) {
    e.preventDefault();
    var productId = $(this).data('product-id');
    deleteFromWishlist(productId);
});

$(document).on('click', '.unfollow-product', function (e) {
    e.preventDefault();
    var productId = $(this).data('product-id');
    unfollowProduct(productId);
});


function deleteBasket(basketId) {
    var csrfToken = document.querySelector('[data-csrf-token]').dataset.csrfToken;
    fetch('/products/basket/delete/' + basketId + '/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                $('#basket-list').html(data.basket_list_html);
                addListenersToInputs(); // Пересоздаем листенеры после обновления HTML-шаблона
            } else {
                console.error('Error when deleting an item from the cart');
            }
        })
        .catch(error => {
            console.error('Error when deleting an item from the cart:', error);
        });
}