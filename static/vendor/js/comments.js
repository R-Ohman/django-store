function limitFileSelection() {
    const input = document.getElementById('files');
    if (input.files.length > 4) {
        showNotification('You can only select up to 4 files.', false);
        // Clear the file input to remove the selected files
        input.value = null;
    }
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === name + '=') {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


function addListenersToInputs() {

    const fileInput = document.querySelector('.custom-file-input');
    const label = document.querySelector('.custom-file-label');

    if (fileInput) {
        fileInput.addEventListener('change', (event) => {
            const files = event.target.files;
            if (files.length === 0) {
                label.textContent = 'Choose files';
            } else {
                let filenames = Array.from(files).map((file) => file.name).join(', ');
                if (filenames.length > 43) {
                    filenames = filenames.substring(0, 40) + '...';
                }
                label.textContent = filenames;
            }
        });
    }

    // Event delegation for handling like/dislike buttons
    $(document).on('click', '.like', function (event) {
        event.preventDefault();
        var button = $(this);
        var commentId = parseInt(button.data('comment-id'), 10);
        var isPositive = button.data('is-positive') === true;
        var url = `/products/comments/like/${commentId}/${isPositive}/`;
        $.ajax({
            url: url,
            type: "POST",
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
            success: function (data) {
                if (data.success) {
                    var ratingElement = $(`#rating-${commentId}`);
                    ratingElement.text(data.rating);
                }
            },
            error: function (xhr, status, error) {
                console.error(error);
            }
        });
    });

    // Initialize Fancybox
    $("[data-fancybox]").fancybox({
        arrows: true, // Display navigation arrows
        infobar: true, // Display image count and caption
        buttons: ["zoom", "slideShow", "fullScreen", "close"], // Customize buttons
        protect: true, // Prevent right-clicking and downloading images
        transitionEffect: "slide", // Set transition effect
    });

    // Close Fancybox when clicking outside the image
    $(document).on("click", ".fancybox-slide, .fancybox-toolbar", function (e) {
        if ($(e.target).hasClass("fancybox-content") || $(e.target).hasClass("fancybox-inner")) {
            $.fancybox.close();
        }
    });


    $(document).on("click", ".fancybox-slide, .fancybox-toolbar", function (e) {
        if ($(e.target).hasClass("fancybox-content") || $(e.target).hasClass("fancybox-inner")) {
            $.fancybox.close();
        }
    });

    $(document).on('click', '.translate', function (event) {
        event.preventDefault(); // Prevent the anchor tag from navigating to the top of the page

        var link = $(this);
        var commentText = link.closest('.card').find('.comment-text');
        var commentId = link.data('comment-id');
        var isTranslated = link.data('translate') === true;

        $.ajax({
            url: "/products/comments/translate/" + commentId + "/",
            type: "GET",
            success: function (response) {
                if (response.success) {
                    if (isTranslated) {
                        commentText.text(response.original_text);
                        link.text(response.message_translate);
                    } else {
                        commentText.text(response.translated_text);
                        link.text(response.message_original);
                    }
                    link.data('translate', !isTranslated);
                }
            },
            error: function (xhr, status, error) {
                console.error(error);
            }
        });
    });


    // Pagination
    function loadComments(page) {
        $.ajax({
            url: window.location.pathname,
            data: {page: page},
            success: function (response) {
                $('#comments-list').html(response.comments_list_html);
                $('#page-list').html(response.page_list_html);
            },
            error: function (xhr, status, error) {
                console.error(error);
            }
        });
    }

    // Use event delegation for handling the click event on pagination links
    $(document).on('click', '.pagination .page-link', function (e) {
        e.preventDefault();
        var page = $(this).data('page');
        loadComments(page);
    });
}

document.addEventListener('DOMContentLoaded', addListenersToInputs);

function submitComment() {
    const form = document.getElementById('comment-form');
    const formData = new FormData(form);

    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(data.message);
                $('#comments').html(data.comments_html);
            } else {
                showNotification(data.message);
            }
        })
        .catch(error => {
            // Обработка ошибки (если нужно)
            console.error(error);
        });
}