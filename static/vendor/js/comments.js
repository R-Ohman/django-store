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

