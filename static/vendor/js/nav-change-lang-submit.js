$(document).ready(function() {
    function bindChangeLanguageEvent() {
        $('label[for^="en"], label[for^="uk"], label[for^="pl"]').click(function() {
            var languageCode = $(this).attr('for');
            var form = $(this).closest('form');
            $('<input>').attr('type', 'hidden').attr('name', 'language').val(languageCode).appendTo(form);
            form.submit();
        });
    }

    bindChangeLanguageEvent();
});
