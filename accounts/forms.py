from django import forms
from .models import ApiKey
class LoginForm(forms.Form):
    fields = ['username', 'password']
    username = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    
class ProfileForm(forms.Form):
    fields = ['first_name', 'last_name', 'email', 'timezone']
    first_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(max_length=150, required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    timezone = forms.CharField(max_length=50, required=True, widget=forms.Select(attrs={'class': 'form-control'}))
    
class PasswordChangeForm(forms.Form):
    fields = ['old_password', 'new_password', 'confirm_password']
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        if new_password != confirm_password:
            raise forms.ValidationError('New password and confirm password do not match.')
        return cleaned_data
    
class ApiKeyForm(forms.Form):
    fields = ['application']
    application = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))

    def save(self, user):
        api_key = ApiKey(user=user, application=self.cleaned_data.get('application'))
