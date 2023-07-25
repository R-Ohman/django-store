// Show/hide password requirements based on user interaction
$(document).ready(function () {
    $('#id_password1').on('focus', function () {
        $('.password-requirements').removeClass('d-none');
    });

    $('#id_password1').on('blur', function () {
        if ($(this).val() === '') {
            $('.password-requirements').addClass('d-none');
        }
    });
});

const togglePasswords = document.querySelectorAll(".togglePassword");
const togglePasswordsArray = Array.from(togglePasswords);

togglePasswordsArray.forEach((togglePassword, index) => {
    togglePassword.addEventListener('click', function (e) {
        const passwordWithIndex = document.querySelector("#id_password" + (index + 1));
        const password = passwordWithIndex ? passwordWithIndex : document.querySelector("#id_password");
        // toggle the type attribute
        const type = password.getAttribute("type") === "password" ? "text" : "password";
        password.setAttribute("type", type);

        // toggle the icon
        this.classList.toggle("bi-eye");
    })
});
