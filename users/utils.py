from deep_translator import GoogleTranslator
from django.urls import reverse


def translate_text_to_user_language(text, request):
    return GoogleTranslator(source='auto', target=request.LANGUAGE_CODE).translate(text)


def translate_text_to_language_by_currency(text, currency):
    return GoogleTranslator(source='auto', target=currency.language).translate(text)

def check_referer_no_keywords(request):
    referer = request.META.get('HTTP_REFERER')
    keywords = [
        reverse('user:registration'),
        reverse('user:reset_password'),
        reverse('user:logout'),
        reverse('user:login'),
    ]
    for keyword in keywords:
        if keyword in referer:
            return False
    return True