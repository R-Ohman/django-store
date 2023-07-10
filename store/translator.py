from deep_translator import GoogleTranslator

def translate_text_to_user_language(text, request):
    return GoogleTranslator(source='auto', target=request.LANGUAGE_CODE).translate(text)
