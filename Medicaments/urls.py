from django.urls import path
from .views import *
from django.urls import include
from django.conf.urls.static import static
from django.conf import settings
from django.shortcuts import redirect
from . import views



urlpatterns = [
    path('home/', views.Affichage.as_view(), name='home'),
    path('ajout/', views.AjoutProduits.as_view(), name='ajout'),
    path('modication/<int:pk>/', views.UpdateDonnees.as_view(), name='modifier'),
    path('delete/<int:pk>/', views.DeleteDonnees.as_view(), name='delete'),
    path('details/<int:pk>/', views.edit.as_view(), name='details'),
    path('recherche/', views.recherche, name='recherche'),
    path('ajoutvente/<int:id>/', views.VenteProduits, name='ajoutvente'),
    path('saverecu/<int:id>/', views.SaveRecu, name='saverecu'),
    path('facture/<int:sale_id>/', views.Facture, name='facture'),
    path("acc/", views.Acc, name="acc"),
    path("historique-ventes/", views.historique_ventes, name="historique_ventes"),

    # ✅ PANIER
    path("panier/", views.panier_view, name="panier"),
    path("panier/ajouter/<int:medoc_id>/", views.ajouter_au_panier, name="ajouter_au_panier"),
    path("panier/supprimer/<int:ligne_id>/", views.supprimer_ligne_panier, name="supprimer_ligne_panier"),
    path("panier/update/", views.update_panier, name="update_panier"),
    path("panier/checkout/", views.checkout_panier, name="checkout_panier"),
    path("panier/valider/", views.valider_panier, name="valider_panier"),
    path("panier/vider/", views.vider_panier, name="vider_panier"),
    path("dashboard/", views.dashboard, name="dashboard"),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)