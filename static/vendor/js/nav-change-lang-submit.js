$(document).ready(function() {
    function bindChangeLanguageEvent() {
        $('label[for^="en"], label[for^="uk"], label[for^="pl"], img[id^="en"], img[id^="uk"], img[id^="pl"]').click(function() {
            var languageCode = $(this).attr('for');
            if (!languageCode) {
                languageCode = $(this).attr('id');
            }
            var form = $(this).closest('form');
            $('<input>').attr('type', 'hidden').attr('name', 'language').val(languageCode).appendTo(form);
            form.submit();
        });
    }

    bindChangeLanguageEvent();
});
