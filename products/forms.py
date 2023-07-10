from django import forms

from store import settings


class ProductAdminForm(forms.ModelForm):
    def clean(self):
        has_name = False
        has_description = False

        cleaned_data = super().clean()
        for lang_code in [lang[0] for lang in settings.LANGUAGES]:
            name = cleaned_data.get(f'name_{lang_code}')
            description = cleaned_data.get(f'description_{lang_code}')

            if name:
                has_name = True
            if description:
                has_description = True

        if not has_name or not has_description:
            raise forms.ValidationError(f'You must fill in at least one of the name fields (name_{lang_code} or description_{lang_code}).')

        return cleaned_data