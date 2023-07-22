from django import template
from users.utils import translate_text_to_user_language

register = template.Library()

@register.filter
def is_foreign_language(comment, request):
    return translate_text_to_user_language(comment.text, request) != comment.text
