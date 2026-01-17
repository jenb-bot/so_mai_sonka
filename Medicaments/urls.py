from django.urls import path
from .views import *
from django.urls import include
from django.conf.urls.static import static
from django.conf import settings
from django.shortcuts import redirect


urlpatterns = [

path('home/', Affichage.as_view(),name='home'),
 path('ajout/', AjoutProduits.as_view(), name='ajout'),
path('modication/<int:pk>/', UpdateDonnees.as_view(), name='modifier'),
 path('delete/<int:pk>/', DeleteDonnees.as_view(),name='delete'),
path('details/<int:pk>/', edit.as_view(),name='details'),
path('recherche/', recherche, name='recherche'),
 path('ajoutvente/<int:id>/', VenteProduits, name='ajoutvente'),
path('saverecu/<int:id>/', SaveRecu, name='saverecu'),
 path('facture/<int:sale_id>/', Facture, name='facture'),
 path("acc/", Acc, name="acc"),
 path("historique-ventes/", historique_ventes, name="historique_ventes"),
    

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 
