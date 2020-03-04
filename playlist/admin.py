from django.contrib import admin

# Register your models here.
from .models import Sugerencia, Cancion, Lista, Video, Bar, Votaciones, Importadas, User, Payments

admin.site.register(Sugerencia)
admin.site.register(Cancion)
admin.site.register(Lista)
admin.site.register(Video)
admin.site.register(Bar)
admin.site.register(Votaciones)
admin.site.register(Importadas)
admin.site.register(User)
admin.site.register(Payments)
