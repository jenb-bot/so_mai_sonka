from django.forms import ModelForm
from .models import Medoc, Vente
from django import forms 


class AjoutProduit(ModelForm):
    class Meta:
        model = Medoc
        fields = [
            'name', 'category', 'price', 'quantite', 'description', 'date_expiration', 'img'
        ]

        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Entrez le nom du produit',
                'class': 'form-control'
            }),

            'category': forms.Select(attrs={
                'class': 'form-control'
            }),

            'price': forms.NumberInput(attrs={
                'placeholder': 'Entrez le prix du produit',
                'class': 'form-control'
            }),

            'quantite': forms.NumberInput(attrs={
                'placeholder': 'Entrez la quantité',
                'class': 'form-control'
            }),

            'description': forms.Textarea(attrs={
                'placeholder': 'Description',
                'class': 'form-control',
                'rows': 4
            }),

            'date_expiration': forms.DateInput(attrs={
                'placeholder': "Date d'expiration",
                'class': 'form-control',
                'type': 'date'
            }),

            'img': forms.ClearableFileInput(attrs={   # ✅ img ici
                'class': 'form-control'
            }),
        }
class AjoutVente(forms.Form):
    customer = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Nom du client"})
    )
    quantite = forms.IntegerField(
        min_value=1,
        required=True,
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "Quantité"})
    )