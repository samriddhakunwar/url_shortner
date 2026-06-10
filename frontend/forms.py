from django import forms
from django.contrib.auth import get_user_model

from shortener.models import ShortURL

User = get_user_model()


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput, min_length=8)
    confirm_password = forms.CharField(widget=forms.PasswordInput, min_length=8)

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("That email is already registered.")
        return email

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username taken.")
        return username

    def clean(self):
        cleaned = super().clean()
        pw = cleaned.get('password')
        confirm = cleaned.get('confirm_password')
        if pw and confirm and pw != confirm:
            self.add_error('confirm_password', "Passwords don't match.")
        return cleaned

    def save(self):
        user = User(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
        )
        user.set_password(self.cleaned_data['password'])
        user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class CreateURLForm(forms.Form):
    original_url = forms.URLField(
        max_length=2048,
        widget=forms.URLInput(attrs={'placeholder': 'https://example.com/some/long/url'})
    )
    custom_alias = forms.CharField(
        max_length=20, required=False,
        help_text="Leave blank to auto-generate. Letters and numbers only."
    )
    expires_at = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        help_text="Optional. The link stops working after this date."
    )

    def clean_custom_alias(self):
        alias = self.cleaned_data.get('custom_alias', '').strip()
        if not alias:
            return ''
        if not alias.isalnum():
            raise forms.ValidationError("Only letters and numbers allowed.")
        if ShortURL.objects.filter(short_code=alias).exists():
            raise forms.ValidationError(f'"{alias}" is already taken.')
        return alias


class EditURLForm(forms.Form):
    original_url = forms.URLField(max_length=2048)
    expires_at = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
    )
