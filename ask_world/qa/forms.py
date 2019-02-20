from django import forms
from . import models
from django.contrib.auth import get_user_model, authenticate

class QuestionModelForm(forms.ModelForm):
    tags = forms.CharField()
    class Meta:
        model = models.Question
        fields = ['title', 'description']

    def clean_tags(self):
        tag_list = [t.strip().lower() for t in tags.split(',')]
        if len(tag_list) < 3:
            raise forms.ValidationError("Add at least three tags")
        return tag_list

    def save(self, commit=True, *args, **qwargs):
        obj = super().save(commit=False, *args, **qwargs)
        if commit: # когда модель сохранена
            tags = [models.Tag.get_or_create(name=t)[0] for t in self.cleaned_data['tags']]
            obj.add(*tags)
        return obj


class UserLoginForm(forms.Form):
    username = forms.CharField(label='Login')
    password = forms.CharField(label='Password')

    def clean(self, *args, **kwargs):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise forms.ValidationError("Invalid credentials")
        return super().clean(*args, **kwargs)


class UserCreationForm(forms.ModelForm):
    avatar = forms.ImageField(
        label='Your photo',
        required=False,
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput,
    )
    password2 = forms.CharField(
        label='Password confirmation',
        widget=forms.PasswordInput,
    )

    class Meta:
        model = get_user_model()
        fields = ('username',)
    
    def clean_password2(self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if len(p1) and p1 != p2:
            raise forms.ValidationError('Passwords don\'t match')
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data.get('password1'))
        if commit:
            user.save()
            Profile.objects.create(user=user, avatar=self.cleaned_data.get('avatar'))
        return user   
