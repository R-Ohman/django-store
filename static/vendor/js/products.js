function getUrlParameter(name) {
    name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
    var regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
    var results = regex.exec(location.search);
    return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
}

function controlFromInput(fromSlider, fromInput, toInput, controlSlider) {
    const [from, to] = getParsed(fromInput, toInput);
    fillSlider(fromInput, toInput, '#C6C6C6', '#2589da', controlSlider);
    if (from > to) {
        fromSlider.value = to;
        fromInput.value = to;
    } else {
        fromSlider.value = from;
    }
}

function controlToInput(toSlider, fromInput, toInput, controlSlider) {
    const [from, to] = getParsed(fromInput, toInput);
    fillSlider(fromInput, toInput, '#C6C6C6', '#2589da', controlSlider);
    setToggleAccessible(toInput);
    if (from <= to) {
        toSlider.value = to;
        toInput.value = to;
    } else {
        toInput.value = from;
    }
}

function controlFromSlider(fromSlider, toSlider, fromInput) {
    const [from, to] = getParsed(fromSlider, toSlider);
    fillSlider(fromSlider, toSlider, '#C6C6C6', '#2589da', toSlider);
    if (from > to) {
        fromSlider.value = to;
        fromInput.value = to;
    } else {
        fromInput.value = from;
    }
}

function controlToSlider(fromSlider, toSlider, toInput) {
    const [from, to] = getParsed(fromSlider, toSlider);
    fillSlider(fromSlider, toSlider, '#C6C6C6', '#2589da', toSlider);
    setToggleAccessible(toSlider);
    if (from <= to) {
        toSlider.value = to;
        toInput.value = to;
    } else {
        toInput.value = from;
        toSlider.value = from;
    }
}

function getParsed(currentFrom, currentTo) {
    const from = parseInt(currentFrom.value, 10);
    const to = parseInt(currentTo.value, 10);
    return [from, to];
}

function fillSlider(from, to, sliderColor, rangeColor, controlSlider) {
    const rangeDistance = to.max - to.min;
    const fromPosition = from.value - to.min;
    const toPosition = to.value - to.min;
    controlSlider.style.background = `linear-gradient(
      to right,
      ${sliderColor} 0%,
      ${sliderColor} ${(fromPosition) / (rangeDistance) * 100}%,
      ${rangeColor} ${((fromPosition) / (rangeDistance)) * 100}%,
      ${rangeColor} ${(toPosition) / (rangeDistance) * 100}%,
      ${sliderColor} ${(toPosition) / (rangeDistance) * 100}%,
      ${sliderColor} 100%)`;
}

function setToggleAccessible(currentTarget) {
    const toSlider = document.querySelector('#toSlider');
    if (Number(currentTarget.value) <= 0) {
        toSlider.style.zIndex = 2;
    } else {
        toSlider.style.zIndex = 0;
    }
}

function addPriceToUrl() {
    const minPrice = document.getElementById('fromSlider').value;
    const maxPrice = document.getElementById('toSlider').value;

    const queryParams = new URLSearchParams(window.location.search);
    queryParams.set('price', `${minPrice}-${maxPrice}`);

    const currentUrl = window.location.href.split('?')[0];
    const newUrl = `${currentUrl}?${queryParams.toString()}`;
    window.location.href = newUrl;
}


$(document).ready(function () {
    // Используем делегирование событий для обработки кликов на кнопках пагинации
    $(document).on('click', '.pagination .page-link', function (e) {
        e.preventDefault();
        var page = $(this).data('page');
        var cat = getUrlParameter('cat');
        loadProducts(page, cat);
    });

    function loadProducts(page, cat) {
        $.ajax({
            url: window.location.pathname,
            data: {page: page, cat: cat},
            success: function (response) {
                $('#product-list').html(response.product_list_html);
                $('#page-list').html(response.page_list_html);
                bindAddToBasketEvent();
            },
            error: function (xhr, status, error) {
                console.error(error);
            }
        });
    }

    function bindAddToBasketEvent() {
        $('.add-to-basket').click(function (e) {
            e.preventDefault();
            var productId = $(this).data('product-id');
            addToBasket(productId);
        });
    }

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

    const fromSlider = document.querySelector('#fromSlider');
    const toSlider = document.querySelector('#toSlider');
    const fromInput = document.querySelector('#fromInput');
    const toInput = document.querySelector('#toInput');
    fillSlider(fromSlider, toSlider, '#C6C6C6', '#2589da', toSlider);
    setToggleAccessible(toSlider);

    fromSlider.oninput = () => controlFromSlider(fromSlider, toSlider, fromInput);
    toSlider.oninput = () => controlToSlider(fromSlider, toSlider, toInput);
    fromInput.oninput = () => controlFromInput(fromSlider, fromInput, toInput, toSlider);
    toInput.oninput = () => controlToInput(toSlider, fromInput, toInput, toSlider);

    document.getElementById('applyFilter').addEventListener('click', addPriceToUrl);
});
