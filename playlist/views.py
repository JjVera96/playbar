from django.shortcuts import render
from django.http import HttpResponse
import httplib2
from oauth2client.contrib import gce
# Create your views here.
from django.shortcuts import redirect
from django.urls import reverse
import sys
import httplib2
from oauth2client.contrib import gce
from googleapiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import OAuth2WebServerFlow
import google.oauth2.credentials
import google_auth_oauthlib.flow
from oauth2client.file import Storage
from django.contrib.auth import authenticate, login, logout, models
import random
from .forms import Registro, Playlist_Form, Login_Form, Sugerencia_Form, Sugerencia_Title_Form, Usuario_Form, Olvidar_Form, Nueva_Password
import re
import qrcode
from .models import Sugerencia, Cancion, Lista, Video, Bar, Votaciones, Importadas, Payments
import json
import time
from datetime import datetime
from datetime import date, time, timedelta
import operator
from django.http import JsonResponse
from django.template import loader
from django.core.mail import send_mail
from django.conf import settings
from random import choice
from django.contrib.auth.hashers import make_password
from django.utils.safestring import mark_safe
import json
from .models import User
from django.views.decorators.csrf import csrf_exempt



def Lading(request):
	if request.user.is_authenticated:
		return redirect("/auth")
	ctx = {}
	return render(request, "index.html", ctx)


def Sign_in(request):
	if request.user.is_authenticated:
		return redirect("/auth")
	login_form = Login_Form(request.POST or None)
	msg = ''
	if login_form.is_valid():
		form_data = login_form.cleaned_data
		username = form_data.get('username')
		password = form_data.get('password')
		try:
			user = User.objects.get(username=username)
		except User.DoesNotExist:
			user = None
		if user is not None:
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user)
				return redirect("/auth")
			else:
				msg = 'Contraseña incorrecta'
		else:
			msg = 'No existe Usuario'

	context = {
		'login_form' : login_form,
		'msg' : msg,
	}
	return render(request, 'singin.html', context)

def Index(request):
	if request.user.is_authenticated:
		if 'credentials' not in request.session:
			return redirect("/auth")
		return redirect("listas")

def Sign_out(request):
	logout(request)
	return redirect("/")

def PlayList(request):
	if request.user.is_authenticated:
		#step1 oauth
		flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
	    'playlist/client_secrets.json',
	    scopes=['https://www.googleapis.com/auth/youtube'])

		#flow.redirect_uri = 'http://127.0.0.1:8000/melo' #LOCAL
		flow.redirect_uri = 'https://eplayt.com/melo'     #REMOTO

		# Generate URL for request to Google's OAuth 2.0 server.
		# Use kwargs to set optional request parameters.
		authorization_url, state = flow.authorization_url(
			# Enable offline access so that you can refresh an access token without
			# re-prompting the user for permission. Recommended for web server apps.
			access_type='offline',
			# Enable incremental authorization. Recommended as a best practice.
			include_granted_scopes='true',
			prompt='consent'
		)
		request.session['state'] = state

		return redirect(authorization_url)
	else:
		return redirect('/')

def Melo(request):
	if request.user.is_authenticated:
		estado = request.GET.get("state")

		flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
		    'playlist/client_secrets.json',
		    scopes=['https://www.googleapis.com/auth/youtube'],
		    state=estado)

		#flow.redirect_uri = 'http://127.0.0.1:8000'+reverse('melo') #LOCAL
		flow.redirect_uri = 'https://eplayt.com'+reverse('melo')     #REMOTO

		authorization_response = request.path
		flow.fetch_token(authorization_response=authorization_response+'?state='+str(request.GET.get("state"))+'&code='+str(request.GET.get("code"))+'&scope=https://www.googleapis.com/auth/youtube')

		# Store the credentials in the session.
		# ACTION ITEM for developers:
		#     Store user's access and refresh tokens in your data store if
		#     incorporating this code into your real app.
		credentials = flow.credentials
		request.session['credentials'] = {
		    'token': credentials.token,
		    'refresh_token': credentials.refresh_token,
		    'token_uri': credentials.token_uri,
		    'client_id': credentials.client_id,
		    'client_secret': credentials.client_secret,
		    'scopes': credentials.scopes
		}
		#print("jeje, estas son mis credenciales",request.session['credentials'])
		return redirect(reverse("listas"))
	else:
		return redirect('/')


@csrf_exempt
def Paypal_return(request):
	return redirect("/listas")

def Listas(request):
	if request.user.is_authenticated:
		ctx = {}
		if 'credentials' not in request.session:
			return redirect("/")

		#load credentials from session
		credentials = google.oauth2.credentials.Credentials(
	      **request.session['credentials'])

		youtube = build('youtube', 'v3', credentials=credentials)

		request.session['credentials'] = {
			'token': credentials.token,
			'refresh_token': credentials.refresh_token,
			'token_uri': credentials.token_uri,
			'client_id': credentials.client_id,
			'client_secret': credentials.client_secret,
			'scopes': credentials.scopes
		}

		if not Payments.objects.filter(customer=request.user):
			return redirect("/payment")
		elif not Payments.objects.filter(customer=request.user)[0].is_active:
			return redirect("/payment")

		try:
			my_playlist = youtube.playlists().list(
				part = "snippet",
				mine = True
				).execute()
		except Exception as e:
			return render(request, "error_cuenta_yt.html", {'e': e})

		importadas = Importadas.objects.filter(bar=request.user)

		elementos = []
		for playlist in my_playlist['items']:
			elemento = {}
			elemento['id'] = playlist['id']
			elemento['title'] = playlist['snippet']['title']
			elementos.append(elemento)

		playlist_form = Playlist_Form(request.POST or None)
		if playlist_form.is_valid():
			form_data = playlist_form.cleaned_data
			url_playlist = form_data.get('url_playlist')
			url, list_id = url_playlist.split('list=')

			if '&' in list_id:
				list_id, index = list_id.split('&', 1)

			playlist_list_request = youtube.playlists().list(
				part="snippet",
				id = list_id
			).execute()

			url = "playlist/{}".format(list_id)
			return redirect(url)

		ctx = {
			'elementos': elementos,
			'importadas': importadas

		}

		return render(request, "list.html", ctx)
	else:
		return redirect('/')



def Playlist(request, id_list):

	if request.user.is_authenticated and Payments.objects.filter(customer=request.user)[0].is_active:
		ctx = {}

		if 'credentials' not in request.session:
			return redirect("/")

		#load credentials from session
		credentials = google.oauth2.credentials.Credentials(
	      **request.session['credentials'])

		youtube = build('youtube', 'v3', credentials=credentials)


		request.session['credentials'] = {
			'token': credentials.token,
			'refresh_token': credentials.refresh_token,
			'token_uri': credentials.token_uri,
			'client_id': credentials.client_id,
			'client_secret': credentials.client_secret,
			'scopes': credentials.scopes
		}
		'''print(request.session['credentials'])
								requestttt = google.auth.transport.requests.Request()
								credentials.refresh(requestttt)'''

		#obtiene la cancion mas votada que se encuentra en la base de datos
		if request.method == 'GET' and request.is_ajax():
			try:
				#most_voted = Votaciones.objects.filter(bar=request.user).order_by('-cantidad')[0].video_id
				voted = Votaciones.objects.filter(bar=request.user).order_by('-cantidad')
				if voted[0].cantidad:
					most_voted = voted[0].video_id
				else:
					most_voted = voted[int(len(voted)/2)].video_id
			except Exception as e:
				most_voted = ''
			return HttpResponse(most_voted)


		if request.method == 'POST' and request.is_ajax():
			Votaciones.objects.filter(bar=request.user).delete()
			params = json.loads(request.body)
			#cambio de cancion
			report_array = params['video_duration']
			videoId = params['video_id']

			instant = datetime.now().time()

			Cancion.objects.create(bar=request.user, duracion=report_array, momento_inicial=instant, video_id=videoId)
			opciones = get_Next_Videos(request.user,5)
			for elem in opciones[1]:
				Votaciones.objects.create(bar=request.user,video_id=elem.video_id,cantidad=0)

		else:
			try:
				playlistitems_list_request = youtube.playlistItems().list(
					playlistId=id_list,
					part="snippet",
					maxResults=50
				).execute()
			except Exception as e:
				print(e)
				#borrar elemento de la base de datos
				return redirect('/errorplaylist')

			videos = Video.objects.all().filter(playlist_id=id_list)
			for video in videos:
				video.delete()

			elementos = []
			for elem in playlistitems_list_request['items']:
				elemento = {}
				elemento['title'] = elem['snippet']['title']
				elemento['videoid'] = video_id=elem['snippet']['resourceId']['videoId']
				elementos.append(elemento)
				ele = Video.objects.create(playlist_id=id_list, video_id=elemento['videoid'], nombre=elemento['title'])

			while 'nextPageToken' in playlistitems_list_request:
				token = playlistitems_list_request['nextPageToken']
				playlistitems_list_request = youtube.playlistItems().list(
					playlistId=id_list,
					part="snippet",
					pageToken = token,
					maxResults=50
				).execute()
				for elem in playlistitems_list_request['items']:
					elemento = {}
					elemento['title'] = elem['snippet']['title']
					elemento['videoid'] = video_id=elem['snippet']['resourceId']['videoId']
					elementos.append(elemento)
					ele = Video.objects.create(playlist_id=id_list, video_id=elemento['videoid'], nombre=elemento['title'])

			playlist_info = youtube.playlists().list(
					part="snippet",
					id = id_list
				).execute()

			title = playlist_info['items'][0]['snippet']['title']
			lis = Lista.objects.create(bar=request.user, playlist_id=id_list, title=title)

			#sugerencias_db = Sugerencia.objects.filter(bar=request.user)
			#sugerencias = get_data_sugerencias(youtube,sugerencias_db,request)

			my_playlist = youtube.playlists().list(
				part = "snippet",
				mine = True
			).execute()
			listas = []
			for playlist in my_playlist['items']:
				listas.append(playlist['id'])

			listas += list(Importadas.objects.filter(bar=request.user).values_list('playlist_id', flat=True))

			if id_list in listas:
				importada = False
			else:
				importada = True


			l = Lista.objects.filter(bar=request.user).order_by('-pk')[0]
			canciones = list(Cancion.objects.filter(bar=request.user, fecha=date.today()).values_list('video_id', flat=True).order_by('-pk'))
			videos = list(Video.objects.filter(playlist_id=l.playlist_id).exclude(video_id__in=canciones))

			if len(videos):
				videoid = videos[random.randrange(0, len(videos))].video_id#['videoid']
			else:
				videoid = ""

			query = Cancion.objects.filter(bar=request.user, fecha=date.today()).count()
			if (len(elementos) == query):
				videoid = ""

			#sonada = Video.objects.filter(video_id=)

			#'videoid' : elementos[random.randrange(0, len(elementos))]['videoid']

			Video.objects.all().exclude(playlist_id=id_list).delete()


			ctx = {
				'importada' : importada,
				'elementos': elementos,
				'title' : title,
				'videoid' : videoid,
				'imported_list': id_list ,
				'cantidad_elementos': len(elementos),
				'credentials': credentials,

			}

		return render(request, "play_list.html", ctx)
	else:
		return redirect('/')

def errorPlaylist(request):
	if request.user.is_authenticated:
		ctx = {}

		if 'credentials' not in request.session:
			return redirect("/")

		#load credentials from session
		credentials = google.oauth2.credentials.Credentials(
	      **request.session['credentials'])

		return render(request, "error_play_list.html", ctx)
	else:
		return redirect('/')

def PlaylistUser(request, bar):

	#elementos para imprimir en la vista de clientes
	try:
		duration_db, name = get_duration_video(bar)
	except Exception as e:
		duration_db, name = 0

	msg = ''
	sugerencia_form = Sugerencia_Form(request.POST or None)

	if sugerencia_form.is_valid():
		print("PlaylistUser")
		form_data = sugerencia_form.cleaned_data
		url = form_data.get("video_id")
		if 'v=' in url:
			rest, videoid = url.split('v=')
		if '.be/' in url:
			rest, videoid = url.split('.be/')

		sug = Sugerencia.objects.create(bar=request.user, video_id=videoid)
		msg = 'Sugerencia agregada'

	if request.method == 'POST' and not request.is_ajax():
		voto = request.POST.get('videos')
		try:
			result = Votaciones.objects.filter(video_id=voto)[0]
			result.cantidad += 1
			result.save()
		except Exception as e:
			pass

	if request.method == 'POST' and request.is_ajax():
		params = json.loads(request.body)
		refrescar_cliente = params['refrescar']
		request.session['refrescar'] = refrescar_cliente


	if request.method == 'GET' and request.is_ajax():
		try:
			flag = request.session['refrescar']
		except Exception as e:
			flag = False
		return HttpResponse(flag)

	elementos = get_Next_Videos(bar, 5)
	ctx = {
		'elementos' : elementos,
		'msg' : msg,
		'video_duration_db': duration_db,
		'name' : name,
		'bar': mark_safe(json.dumps(bar))
	}

	return render(request, "user.html", ctx)

def get_Next_Videos(bar, cantidad):
	try:
		l = Lista.objects.filter(bar=bar).order_by('-pk')[0]
	except Exception as e:
		return (True, "Es posible que en este momento no se esté reproduciendo ninguna canción en el bar, asegurate de esto y refresca tu navegador")


	canciones = list(Cancion.objects.filter(bar=bar, fecha=date.today()).values_list('video_id', flat=True).order_by('-pk'))

	try:
		ultima_cancion = canciones.pop(0)
	except Exception as e:
		return (True, "Es posible que en este momento no se esté reproduciendo ninguna canción en el bar, asegurate de esto y refresca tu navegador")


	videos = Video.objects.filter(playlist_id=l.playlist_id).exclude(video_id__in=canciones)

	if cantidad < len(videos):
		total = len(videos)
		indices = list(videos.values_list('video_id', flat=True))
		try:
			indice_ultima = indices.index(ultima_cancion)
		except Exception as e:
			return (True, "Refrescar navegador")

		videos = list(videos)

		if indice_ultima == 0:
			videos = videos[:cantidad+1]
			videos.pop(0)

		elif indice_ultima == total-1:
			videos = videos[total-cantidad-1:]
			videos.pop(-1)

		elif indice_ultima - cantidad/2 <= 0:
			videos = videos[:cantidad+1]
			videos.pop(indice_ultima)

		elif indice_ultima + cantidad/2 >= total-1:
			videos = videos[total-cantidad-1:]
			videos.pop(indice_ultima-1)
		else:
			inicio = indice_ultima-int(cantidad/2)
			if cantidad%2==0:
				fin = indice_ultima+cantidad/2
			else:
				fin = indice_ultima+int(cantidad/2)+2
			videos =  videos[inicio:fin]
			videos.pop(int(len(videos)/2-1))
	else:
		indices = list(videos.values_list('video_id', flat=True))
		if (len(indices) != 0 ):
			try:
				indice_ultima = indices.index(ultima_cancion)
				videos = list(videos)
				videos.pop(indice_ultima)
			except Exception as e:
				videos = list(videos)

	return (False, videos)


def Cuenta(request):
	if request.user.is_authenticated and Payments.objects.filter(customer=request.user)[0].is_active:
		msg_usuario = ''
		msg_password = ''

		if (request.user.qr == ""):
			qr = qrcode.QRCode(
				version = 1,
				error_correction = qrcode.constants.ERROR_CORRECT_H,
				box_size = 10,
				border = 4,
			)
			qr.add_data('https://eplayt.com/user/{}'.format(request.user))
			img = qr.make_image()
			name = 'images/qr/{}.png'.format(request.user)
			img.save('media/' + name, 'png')
			request.user.qr = name
			request.user.save()


		logo = request.user.logo

		usuario_form = Usuario_Form(request.POST or None, request.FILES or None, instance=request.user)
		nueva_password = Nueva_Password(request.POST or None)

		if nueva_password.is_valid():
			form_data = nueva_password.cleaned_data
			password_actual = form_data.get("password_actual")
			password_nueva = form_data.get("password_nueva")
			password_confirmar = form_data.get("password_confirmar")
			acceso = authenticate(username=request.user.username, password=password_actual)
			if acceso is not None:
				if password_nueva == password_confirmar:
					request.user.password = make_password(password_nueva, salt=None, hasher='default')
					request.user.save()
					msg_password = 'Contraseña actualizada satisfactoriamente'
				else:
					msg_password = 'Las contraseñas nueva y la confirmacion no coinciden'
			else:
				msg_password = 'Contraseña incorrecta'

		if usuario_form.is_valid():
			form_data = usuario_form.cleaned_data
			request.user.email = form_data.get("email")
			request.user.first_name = form_data.get("first_name")
			request.user.logo = form_data.get("logo")
			request.user.save()
			msg_usuario = 'Usuario actualizado satisfactoriamente'


		ctx = {
			'usuario_form' : usuario_form,
			'nueva_password' : nueva_password,
			'msg_usuario' : msg_usuario,
			'msg_password' : msg_password
		}

		return render(request, "cuenta.html", ctx)
	else:
		return redirect('/')

def Registrar(request):
	register_form = Registro(request.POST or None)

	if register_form.is_valid():
		form_data = register_form.cleaned_data
		user = form_data.get('username')
		try:
			user = User.objects.get(username=user)
		except User.DoesNotExist:
			user = None

		if user is None:
			username = form_data.get("username")
			print(username)
			email = form_data.get("email")
			print(email)
			first_name = form_data.get("first_name")
			print(first_name)
			last_name = form_data.get("last_name")
			print(last_name)
			pword = form_data.get("password")
			print(pword)
			password = make_password(pword, salt=None, hasher='default')
			print(password)
			ciudad = form_data.get("ciudad")
			print(ciudad)
			name_place = form_data.get("name_place")
			print(name_place)
			user = User.objects.create(username=username, password=password, email=email, first_name=first_name, last_name=last_name, ciudad=ciudad, name_place=name_place, is_active=True)
			print("guardado")
			return redirect("/")

	ctx = {'register_form': register_form}
	return render(request, "registrar.html", ctx)

def get_duration_video(bar):
	from_db = Cancion.objects.filter(bar=bar).order_by('-pk')
	t1 = datetime.combine(date.min, from_db[0].momento_inicial) - datetime.min
	t2 = datetime.combine(date.min, datetime.now().time()) - datetime.min
	resta = t2.total_seconds() -  t1.total_seconds()
	duration_db = from_db[0].duracion - resta
	if duration_db <= 0:
		duration_db = 0

	try:
		name = Video.objects.filter(video_id=from_db[0].video_id).values_list('nombre', flat=True)[0]
	except:
		name = ''

	return duration_db, name

def Delete_imported(request, id_list):
	Importadas.objects.filter(playlist_id=id_list)[0].delete()
	return redirect('/listas')

def Save_imported_pl(request):
	if request.user.is_authenticated:
		ctx = {}

		if 'credentials' not in request.session:
			return redirect("/")

		#load credentials from session
		credentials = google.oauth2.credentials.Credentials(
	      **request.session['credentials'])

		youtube = build('youtube', 'v3', credentials=credentials)
		if request.method == 'POST' and request.is_ajax():
			params = json.loads(request.body)

			playlist_id = params['playlist_id']

			playlist_imported_info = youtube.playlists().list(
				part="snippet",
				id = playlist_id
			).execute()
			title_imported = playlist_imported_info['items'][0]['snippet']['title']
			autor_imported = playlist_imported_info['items'][0]['snippet']['channelTitle']
			no_imported_canciones = params['cantidad_elementos']

			Importadas.objects.create(bar=request.user,playlist_id=playlist_id,title=title_imported,autor=autor_imported,no_canciones=no_imported_canciones)
		return JsonResponse({})
	else:
		return redirect("/")

def Accept_sugerencia(request, id_list):
	params = json.loads(request.body)
	video_id = params['video_id']

	if(Video.objects.filter(playlist_id=id_list, video_id=video_id)):
		Sugerencia.objects.filter(video_id=video_id, bar=request.user).delete()
		return JsonResponse({})


	credentials = google.oauth2.credentials.Credentials(**request.session['credentials'])
	youtube = build('youtube', 'v3', credentials=credentials)
	info = youtube.videos().list(
		part = "snippet",
		id = video_id
	).execute()
	Video.objects.create(playlist_id=id_list,video_id=video_id,nombre=info['items'][0]['snippet']['title'])
	Sugerencia.objects.filter(video_id=video_id, bar=request.user).delete()
	return redirect("/ajax/load_sugerencia/")

def Deny_sugerencia(request):
	params = json.loads(request.body)
	video_id = params['video_id']
	Sugerencia.objects.filter(video_id=video_id, bar=request.user).delete()
	return redirect("/ajax/load_sugerencia/")

def Load_videos(request, id_list):
	videos = Video.objects.filter(playlist_id=id_list)
	template = loader.get_template('videos_playlist.html')
	return HttpResponse(template.render({'elementos': videos}, request))

def Load_sugerencias(request):
	credentials = google.oauth2.credentials.Credentials(**request.session['credentials'])
	youtube = build('youtube', 'v3', credentials=credentials)

	sug_no_info = Sugerencia.objects.filter(bar=request.user, thumbnail="", title="", channel="")
	sug_no_id = Sugerencia.objects.filter(bar=request.user, thumbnail="", channel="")

	if sug_no_id:
		for elem_info in sug_no_id:
			if not elem_info.video_id:
				response = youtube.search().list(
				    part='snippet',
				    maxResults=1,
				    q=elem_info.title,
				    type=''
				).execute()
				if response['pageInfo']['totalResults'] == 0:
					elem_info.delete()
				else:
					elem_info.thumbnail = response['items'][0]['snippet']['thumbnails']['default']['url']
					elem_info.video_id = response['items'][0]['id']['videoId']
					elem_info.title = response['items'][0]['snippet']['title']
					elem_info.channel = response['items'][0]['snippet']['channelTitle']
					elem_info.save()


	if(sug_no_info):
		for elem_info in sug_no_info:
			info = youtube.videos().list(
				part = "snippet",
				id = elem_info.video_id
			).execute()
			item = Sugerencia.objects.filter(bar=request.user, video_id=elem_info.video_id)[0]
			item.thumbnail = info['items'][0]['snippet']['thumbnails']['default']['url']
			item.title = info['items'][0]['snippet']['title']
			item.channel = info['items'][0]['snippet']['channelTitle']
			item.save()

	sugerencias = Sugerencia.objects.filter(bar=request.user)
	print_info = {}
	if(sugerencias):
		for elem in sugerencias:
			print_info[elem.video_id] = (elem.title, elem.channel, elem.thumbnail)

	template = loader.get_template('sugerencias_ajax.html')
	return HttpResponse(template.render({'sugerencias': print_info}, request))


def Send_sugerencia_cliente(request, bar):
	sugerencia_form = Sugerencia_Form(request.POST or None)
	sugerencia_title = Sugerencia_Title_Form(request.POST or None)

	if sugerencia_title.is_valid():
		form_data_title = sugerencia_title.cleaned_data
		title_name = form_data_title.get('titulo_video')
		sug_title = Sugerencia.objects.create(bar=request.user, title=title_name)
		msg = 'Sugerencia agregada'
		return JsonResponse({'mensaje': "Sugerencia enviada correctamente al admnistrador "})


	if sugerencia_form.is_valid():
		form_data = sugerencia_form.cleaned_data
		url = form_data.get("video_id")
		if 'v=' in url:
			rest, videoid = url.split('v=')
		if '.be/' in url:
			rest, videoid = url.split('.be/')

		if(Sugerencia.objects.filter(bar=bar, video_id=videoid)):
			return JsonResponse({'mensaje': "Tu cancion ya está siendo aprobada por el admnistrador"})

		Sugerencia.objects.create(bar=bar, video_id=videoid, thumbnail="", title="", channel="")
		return JsonResponse({'mensaje': "Sugerencia enviada correctamente al admnistrador "})

	return JsonResponse({'mensaje': "Error en la solicitud"})

def Olvidar_Cuenta(request):
	if request.user.is_authenticated:
		return redirect('/')

	msg = ""
	olvidar_form = Olvidar_Form(request.POST or None)
	if olvidar_form.is_valid():
		form_data = olvidar_form.cleaned_data
		email = form_data.get('email')
		try:
			user = User.objects.get(email=email)
		except User.DoesNotExist:
			user = None

		if user is not None:
			valores = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
			password = ""
			new_password = password.join([choice(valores) for i in range(8)])
			password = new_password
			new_password = make_password(password, salt=None, hasher='default')
			user.password = new_password
			user.save()
			send_password(1, user, password)
			msg = "Te hemos enviado un correo con tu nueva contraseña de ingreso. Revisa tu bandeja de entrada"
		else:
			msg = "No hay usuario con este email. Por favor registrate"

	ctx = {
		'olvidar_form' : olvidar_form,
		'msg' : msg
	}

	return render(request, "olvidar_cuenta.html", ctx)

def send_password(mode, user, password):
	if mode == 0:
		title = 'Registro en ePlayt'
		body = "Genial! Registro Completado\nBienvenido {} {}\nTu contraseña de ingreso es {}".format(user.first_name, user.last_name, password)
	else:
		title = "Recuperacion Contraseña en ePlayt"
		body = "Hola {} {}\nTu nueva contraseña de ingreso es {}".format(user.first_name, user.last_name, password)
	send_mail(
		title,
		body,
	 	settings.EMAIL_HOST_USER,
		[user.email, 'jjvera96@gmail.com'],
		fail_silently=False,
	)
