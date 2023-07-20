function limitFileSelection() {
    const input = document.getElementById('files');
    if (input.files.length > 4) {
        showNotification('You can only select up to 4 files.', false);
        // Clear the file input to remove the selected files
        input.value = null;
    }
}