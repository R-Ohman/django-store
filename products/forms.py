from django import forms

from products.models import Product
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

        # or not has_description
        if not has_name:
            raise forms.ValidationError(f'You must fill in at least one of the name fields.')

        return cleaned_data

    name_en = forms.CharField(
        label='Name',
        widget=forms.Textarea(attrs={'rows': 2, 'cols': 140}),
        required=False,
    )

    name_uk = name_pl = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'cols': 50}),
        required=False,
    )

    description_en = forms.CharField(
        label='Description',
        widget=forms.Textarea(attrs={'rows': 4, 'cols': 140}),
        required=False,
    )

    description_uk = description_pl = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 8, 'cols': 50}),
        required=False,
    )

    class Meta:
        model = Product
        fields = '__all__'
