from django.db.models.signals import pre_save
from django.dispatch import receiver
from products.models import Product, ProductCategory
from store import settings
from deep_translator import GoogleTranslator
from django.conf import settings
from modeltranslation.translator import translator, NotRegistered
from modeltranslation.utils import build_localized_fieldname


def translate_fields(sender, instance, **kwargs):
    try:
        # Получаем список полей для перевода модели
        translation_fields = translator.get_options_for_model(sender).get_field_names()

        # Проходимся по всем полям перевода
        for field_name in translation_fields:
            value = None
            value_language = None
            # ищем не пустое поле
            for lang_code, _ in settings.LANGUAGES:
                localized_field_name = build_localized_fieldname(field_name, lang_code)
                if getattr(instance, localized_field_name):
                    value = getattr(instance, localized_field_name)
                    value_language = lang_code
                    break

            if not value:
                continue

            # Итерируемся по всем языкам
            for lang_code, _ in settings.LANGUAGES:
                localized_field_name = build_localized_fieldname(field_name, lang_code)

                # если поле заполнено, скип
                if getattr(instance, localized_field_name):
                    continue

                translated_value = GoogleTranslator(source=value_language, target=lang_code).translate(value)

                if field_name == 'name':
                    translated_value = translated_value.title()

                # Устанавливаем переведенное значение в localized_field_name экземпляра
                setattr(instance, localized_field_name, translated_value)

    except NotRegistered:
        pass

# Регистрируем signal handler для модели Product
@receiver(pre_save, sender=Product)
def auto_fill_translation_fields_product(sender, instance, **kwargs):
    translate_fields(sender, instance, **kwargs)

# Регистрируем signal handler для модели ProductCategory
@receiver(pre_save, sender=ProductCategory)
def auto_fill_translation_fields_product_category(sender, instance, **kwargs):
    translate_fields(sender, instance, **kwargs)
