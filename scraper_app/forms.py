from django import forms

class BusquedaForm(forms.Form):
    palabra_clave = forms.CharField(
        label='Palabra Clave Educativa', 
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )