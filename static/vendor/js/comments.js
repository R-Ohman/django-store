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

    const likeButtons = document.querySelectorAll('.like');
    likeButtons.forEach((button) => {
        button.addEventListener('click', (event) => {
            event.preventDefault();
            const commentId = parseInt(button.dataset.commentId, 10);
            const isPositive = button.dataset.isPositive === 'true';
            const url = `/products/comments/like/${commentId}/${isPositive}/`;
            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'), // Ensure you have a function to get the CSRF token
                },
            })
                .then((response) => response.json())
                .then((data) => {
                    if (data.success) {
                        const ratingElement = document.querySelector(`#rating-${commentId}`);
                        ratingElement.textContent = data.rating;
                    }
                })
                .catch((error) => console.error('Error:', error));
        });
    });
}

document.addEventListener('DOMContentLoaded', addListenersToInputs);

$(document).ready(function () {
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
});

// Initialize Fancybox
$("[data-fancybox]").fancybox({
    arrows: true,
    infobar: true,
    buttons: ["zoom", "slideShow", "fullScreen", "close"],
    protect: true,
    transitionEffect: "slide",
});

// Close Fancybox when clicking outside the image
$(document).on("click", ".fancybox-slide, .fancybox-toolbar", function (e) {
    if ($(e.target).hasClass("fancybox-content") || $(e.target).hasClass("fancybox-inner")) {
        $.fancybox.close();
    }
});
