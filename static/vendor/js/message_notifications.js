document.addEventListener('DOMContentLoaded', function() {
  var messages_suc = document.querySelectorAll('.message-success');
  var messages_err = document.querySelectorAll('.message-error');
  messages_suc.forEach(function(message) {
    showNotification(message.textContent, true);
  });
  messages_err.forEach(function(message) {
    showNotification(message.textContent, false);
  });
});

function showNotification(message, success=true) {
  toastr.options = {
    "progressBar": true,
    "positionClass": "toast-bottom-left",
    "timeOut": "3000",
  };
  if (success) {
    toastr.success(message);
  } else {
    toastr.warning(message);
  }
}