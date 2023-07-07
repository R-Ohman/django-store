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
      },
      error: function(xhr, status, error) {
        console.error(error);
      }
    });
  }
});
