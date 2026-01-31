from django.contrib.auth.signals import user_logged_out
from django.dispatch import receiver
from .models import Panier

@receiver(user_logged_out)
def fermer_panier_a_la_deconnexion(sender, request, user, **kwargs):
    Panier.objects.filter(user=user, is_active=True).update(is_active=False)
