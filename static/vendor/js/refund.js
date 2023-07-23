function limitFileSelection() {
    const input = document.getElementById('files');
    if (input.files.length > 6) {
        showNotification('You can only select up to 6 files.', false);
        // Clear the file input to remove the selected files
        input.value = null;
    }
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
}

document.addEventListener('DOMContentLoaded', addListenersToInputs);
