$(document).ready(function() {
        $('label[for^="en"], label[for^="uk"], label[for^="pl"]').click(function() {
            var languageCode = $(this).attr('for');
            $('<input>').attr('type', 'hidden').attr('name', 'language').val(languageCode).appendTo('form');
            $('form').submit();
        });
    });
