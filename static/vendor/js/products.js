$(document).ready(function() {
  // Используем делегирование событий для обработки кликов на кнопках пагинации
  $(document).on('click', '.pagination .page-link', function(e) {
    e.preventDefault();
    var page = $(this).data('page');
    loadProducts(page);
  });

  function loadProducts(page) {
    $.ajax({
      url: window.location.pathname,
      data: { page: page },
      success: function(response) {
        $('#product-list').html(response.product_list_html);
        $('#page-list').html(response.page_list_html);
        // После обновления контента привязываем событие click для кнопок добавления в корзину
        bindAddToBasketEvent();
      },
      error: function(xhr, status, error) {
        console.error(error);
      }
    });
  }

  function bindAddToBasketEvent() {
    $('.add-to-basket').click(function(e) {
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
            throw new Error('Ошибка при добавлении товара в корзину');
          }
        })
        .then(data => {
          if (data.success) {
            showNotification(data.product_name + ' успешно добавлен в корзину');
          } else {
            showNotification('Ошибка при добавлении товара в корзину', success=false);
          }
        })
        .catch(error => {
          console.error(error);
          showNotification('Необходима авторизация', success=false);
          window.location.href = '/user/login/'; // Перенаправляем пользователя на страницу входа
        });
    }


  function showNotification(message, success=true) {
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

  // При первоначальной загрузке страницы также привязываем событие click для кнопок добавления в корзину
  bindAddToBasketEvent();
});
