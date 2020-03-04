# -*- coding: utf-8 -*-
from django import forms
from .models import Sugerencia, User

class Playlist_Form(forms.Form):
	url_playlist = forms.CharField(max_length=100)

class Login_Form(forms.Form):
	username = forms.CharField(max_length=50)
	password = forms.CharField(max_length=50)
	
class Vote_song(forms.Form):
	url_playlist = forms.CharField(max_length=72)

class Sugerencia_Form(forms.ModelForm):
	class Meta:
		model = Sugerencia
		fields = ["video_id"]

class Sugerencia_Title_Form(forms.Form):
	titulo_video = forms.CharField(max_length=200)

class Usuario_Form(forms.ModelForm):
	class Meta:
		model = User
		fields = ["email", "first_name", "logo"]

class Olvidar_Form(forms.Form):
	email = forms.EmailField(max_length=50)

class Nueva_Password(forms.Form):
	password_actual = forms.CharField(max_length=50)
	password_nueva = forms.CharField(max_length=50)
	password_confirmar = forms.CharField(max_length=50)

class Registro(forms.ModelForm):
	class Meta:
		model = User
		fields=['username', 'password', 'email', 'first_name', 'last_name', 'ciudad', 'name_place']


