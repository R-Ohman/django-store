from deep_translator import GoogleTranslator


def translate_text_to_user_language(text, request):
    print(request.LANGUAGE_CODE)
    return GoogleTranslator(source='auto', target=request.LANGUAGE_CODE).translate(text)


def translate_text_to_language(text, language_code):
    return GoogleTranslator(source='auto', target=language_code.lower()).translate(text)


def translate_text_to_language_by_currency(text, currency):
    return GoogleTranslator(source='auto', target=currency.language).translate(text)
