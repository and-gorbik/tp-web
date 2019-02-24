from django.test import TestCase
from django.contrib.auth import get_user_model
from qa.models import Profile
from qa import forms

class QuestionFormTestCase(TestCase):

    def test_valid_form(self):
        data = {
            'title': 'A new question',
            'description': 'Text',
            'tags': "good  , bad, Angry    ",
        }
        form = forms.QuestionForm(data=data) # QuestionForm(request.POST)
        self.assertTrue(form.is_valid())
        tags = form.cleaned_data.get('tags')
        for t in tags:
            self.assertIn(t, ['good', 'bad', 'angry'])

    def test_invalid_form(self):
        data = {
            'tags': "good",
        }
        form = forms.QuestionForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors)


class UserLoginFormTestCase(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user('Andrey', password='12345')
        Profile.objects.create(user=user)

    def test_valid_form(self):
        data = {
            'username': 'Andrey',
            'password': '12345',
        }
        form = forms.UserLoginForm(data=data)
        self.assertTrue(form.is_valid())

class UserCreationFormTestCase(TestCase):
    def test_not_equal_passwords(self):
        data = {
            'username': 'Andrey',
            'password1': '12345',
            'password2': '',
        }
        form = forms.UserCreationForm(data=data)
        self.assertFalse(form.is_valid())