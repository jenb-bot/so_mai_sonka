from django.contrib import admin

from .models import *
admin.site.register(Categories)
admin.site.register(Vente)
admin.site.register(Facture_client)
admin.site.register(Customer)
admin.site.register(Medoc)
admin.site.register(Panier)
admin.site.register(LignePanier)
