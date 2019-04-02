from django import forms
from django.contrib.auth.models import User

from blog.models import Capsule, Comment, Profile


class ArticleForm(forms.ModelForm):

    class Meta:
        model = Capsule
        exclude = ('fileItem', 'user','author','average','slug', 'views', 'date')


class UserFormSignUp(forms.Form):
    pseudo = forms.CharField(max_length=60)
    adresse_mail = forms.EmailField(label="Votre adresse Email")
    password = forms.CharField(max_length=32, widget=forms.PasswordInput)
    first_name = forms.CharField(max_length=50, label="Votre prénom")
    last_name = forms.CharField(max_length=50, label="Votre nom")
    CLUF = forms.CheckboxInput()


class UserLogIn(forms.Form):
    pseudo = forms.CharField(max_length=60)
    password = forms.CharField(max_length=32, widget=forms.PasswordInput)



class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = '__all__'

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = 'picture','city',

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = 'username', 'email', 'password', 'first_name', 'last_name'
        widgets = {
            'password': forms.PasswordInput(),
        }


class UserFormUpdate(forms.ModelForm):
    class Meta:
        model = User
        fields = 'username', 'email', 'first_name', 'last_name'


class form_reset_password_create(forms.Form):
    email = forms.EmailField(max_length=100)


class form_reset_password_confirm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput)
    re_new_password = forms.CharField(widget=forms.PasswordInput)

class upate_profile_form(forms.ModelForm):
    class Meta:
        model = User
        fields = 'username', 'email', 'first_name', 'last_name'

class Contact(forms.Form):
    sujet = forms.CharField(max_length=256)
    email = forms.EmailField()
    message = forms.CharField()
