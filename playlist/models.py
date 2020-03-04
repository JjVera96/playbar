from django.db import models
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from .managers import UserManager
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.timezone import now


class User(AbstractBaseUser, PermissionsMixin):
	username = models.CharField(primary_key=True, max_length=50, unique=True)
	email = models.EmailField(unique=True)
	first_name = models.CharField(max_length=50)
	second_name = models.CharField(max_length=50, blank=True)
	last_name = models.CharField(max_length=50)
	second_last_name = models.CharField(max_length=50, blank=True)
	date_joined = models.DateTimeField(auto_now_add=True)
	is_staff = models.BooleanField(default=False)
	is_active = models.BooleanField(default=False)
	qr = models.ImageField(upload_to='images/qr', blank=True)
	logo = models.ImageField(upload_to='images/bares', blank=True)
	ciudad = models.CharField(max_length=100, blank=True)
	expiration = models.BooleanField(default=False)
	expiration_date = models.DateTimeField(default=datetime.now)
	name_place = models.CharField(max_length=50)

	objects = UserManager()

	USERNAME_FIELD = 'username'
	REQUIRED_FIELDS = ["email"]

	class Meta:
		verbose_name = u'Usuario'
		verbose_name_plural = u'Usuarios'

	def get_full_name(self):
		full_name = '%s %s' % (self.first_name, self.last_name)
		return full_name.strip()

	def get_short_name(self):
		return self.first_name

class Payments(models.Model):
	class Meta:
		verbose_name = u"Payment"
		verbose_name_plural  = u"Payments"

	customer = models.ForeignKey(User, on_delete=models.CASCADE)
	payment_date = models.DateTimeField(default=datetime.now)
	payment_expiration = models.DateTimeField(blank=True, null=True)
	is_active = models.BooleanField(default=True)

# Create your models here.
class Sugerencia(models.Model):
	class Meta:
		verbose_name = u"Sugerencia"
		verbose_name_plural  = u"Sugerencias"

	bar = models.CharField(max_length=50)
	video_id = models.CharField(max_length=50)
	thumbnail = models.CharField(max_length=300)
	title = models.CharField(max_length=100)
	channel = models.CharField(max_length=100)


class Cancion(models.Model):
	class Meta:
		verbose_name = u"Cancion"
		verbose_name_plural  = u"Canciones"

	bar = models.CharField(max_length=50)
	duracion = models.IntegerField(default=0)#segundos
	video_id = models.CharField(max_length=100)
	momento_inicial = models.TimeField(default=datetime.now)#datatime
	fecha = models.DateField(auto_now_add=True)

class Lista(models.Model):
	class Meta:
		verbose_name = u"Lista Sonada"
		verbose_name_plural  = u"Lista Sonadas"

	bar = models.CharField(max_length=50)
	playlist_id = models.CharField(max_length=50)
	title = models.CharField(max_length=100)

class Video(models.Model):
	class Meta:
		verbose_name = u"Video"
		verbose_name_plural  = u"Videos"

	playlist_id = models.CharField(max_length=50)
	video_id = models.CharField(max_length=50)
	nombre = models.CharField(max_length=100)

class Bar(models.Model):
	class Meta:
		verbose_name = u"Bar"
		verbose_name_plural  = u"Bares"

	user = models.OneToOneField(User, on_delete=models.CASCADE)
	qr = models.ImageField(upload_to='images/qr', blank=True)
	logo = models.ImageField(upload_to='images/bares', blank=True)
	ciudad = models.CharField(max_length=100)

	def __str__(self):
		return str(self.user.username)

class Votaciones(models.Model):
	class Meta:
		verbose_name = u"Votacion"
		verbose_name_plural  = u"Votaciones"

	bar = models.CharField(max_length=50)
	video_id = models.CharField(max_length=50)
	cantidad = models.IntegerField(default=0)

class Importadas(models.Model):
	class Meta:
		verbose_name = u"Lista Importada"
		verbose_name_plural  = u"Listas Importadas"

	bar = models.CharField(max_length=50)
	playlist_id = models.CharField(max_length=50)
	title = models.CharField(max_length=100)
	autor = models.CharField(max_length=100)
	no_canciones = models.IntegerField(default=0)
