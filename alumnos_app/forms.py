from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True) # Hacemos el email requerido

    class Meta:
        model = User
        # username, email y password (viene del UserCreationForm)
        fields = ("username", "email")

    # Sobreescribimos el metodo save para asegurar que el email se guarde
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user