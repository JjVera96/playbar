from django.urls import path, re_path
from playlist import views
from django.conf.urls import url, include
from grap_main import views as views2

urlpatterns = [
    path('', views.Lading, name="lading"),
    path('sign_in', views.Sign_in, name="sign_in"),
    path('sign_out', views.Sign_out, name="sign_out"),
    path('auth', views.PlayList, name = "auth"),
    path('melo', views.Melo, name="melo"),
    path('index', views.Index, name="index"),
    path('listas', views.Listas, name="listas"),
    path('paypal_return', views.Paypal_return, name="paypal_return"),
    re_path('playlist/(?P<id_list>[\w-]+)/$', views.Playlist, name="playlist"),
    path('errorplaylist', views.errorPlaylist, name="errorplaylist"),
    re_path('user/(?P<bar>[\w-]+)/$',views.PlaylistUser, name="user"),
    path('cuenta', views.Cuenta, name="cuenta"),
    path('registrar', views.Registrar, name="registrar"),
    re_path('delete_list/(?P<id_list>[\w-]+)/$', views.Delete_imported, name="delete_list"),
    #path('melo/<state>/<code>', views.Melo, name="melo"),
    path('ajax/save_imported/', views.Save_imported_pl, name='save_imported_pl'),
    re_path('ajax/accept_sugerencia/(?P<id_list>[\w-]+)/$', views.Accept_sugerencia, name='accept_sugerencia'),
    path('ajax/deny_sugerencia/', views.Deny_sugerencia, name='deny_sugerencia'),
    path('ajax/load_sugerencia/', views.Load_sugerencias, name='load_sugerencia'),
    re_path('ajax/send_sugerencia_cliente/(?P<bar>[\w-]+)/$', views.Send_sugerencia_cliente, name='send_sugerencia_cliente'),
    re_path('ajax/load_videos/(?P<id_list>[\w-]+)/$', views.Load_videos, name='load_videos'),
    path('olvidar_cuenta/', views.Olvidar_Cuenta, name='olvidar_cuenta'),

    path('payment', views2.view_that_asks_for_money, name='payment'),

    url(r'^paypal/', include('paypal.standard.ipn.urls')),

]
