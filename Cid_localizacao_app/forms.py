from django import forms
from .models import Relatorio

class RelatorioForm(forms.ModelForm):
    class Meta:
        model = Relatorio
        fields = ['data', 'relatorio']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date', 'class': 'short-date-input'}),
        }

