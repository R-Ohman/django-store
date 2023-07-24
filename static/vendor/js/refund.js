function limitFileSelection() {
    const input = document.getElementById('files');
    if (input.files.length > 6) {
        showNotification('You can only select up to 6 files.', false);
        // Clear the file input to remove the selected files
        input.value = null;
    }
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

function handleFormSubmit() {
    const form = document.getElementById('refund-form');
    const orderItems = document.querySelectorAll('.order-item');

    orderItems.forEach((orderItem) => {
        const checkbox = orderItem.querySelector('.form-check-input');
        const quantityField = orderItem.querySelector('.quantity-field');
        const reasonField = orderItem.querySelector('.reason-field');

        checkbox.addEventListener('change', () => {
            if (checkbox.checked) {
                quantityField.style.display = 'block';
                reasonField.style.display = 'block';
                // Включить скрытые поля
                quantityField.querySelector('input').disabled = false;
                reasonField.querySelector('select').disabled = false;
            } else {
                quantityField.style.display = 'none';
                reasonField.style.display = 'none';
                // Отключить поля перед отправкой формы
                quantityField.querySelector('input').disabled = true;
                reasonField.querySelector('select').disabled = true;
            }
        });
    });


    form.addEventListener('submit', (event) => {
        const checkedCheckboxes = form.querySelectorAll('.form-check-input:checked');
        if (checkedCheckboxes.length === 0) {
            event.preventDefault();
            showNotification("Please select at least one item to refund.", false);
        } else {
            const hiddenFields = form.querySelectorAll('[disabled]');
            hiddenFields.forEach((field) => field.remove());
        }
    });
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

    handleFormSubmit();
}

document.addEventListener('DOMContentLoaded', addListenersToInputs);
