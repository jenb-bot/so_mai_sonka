from django.shortcuts import render, get_object_or_404 , redirect
from decimal import Decimal
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from .models import *
from .forms import AjoutProduit
from .forms import AjoutProduit, AjoutVente



# -----------------------------
# LISTE / AFFICHAGE DES PRODUITS
# -----------------------------

class Affichage(LoginRequiredMixin,ListView):
    model = Medoc
    template_name = "Medicaments/home.html"
    queryset = Medoc.objects.all()
    context_object_name = "donnees"  # dans le template: {% for n in donnees %}

#affichage apres la page de connexion

@login_required(login_url='login')
def Acc(request):

    return render(request, 'Medicaments/acc.html')
# -----------------------------
# AJOUT PRODUIT
# -----------------------------
class AjoutProduits(CreateView):
    model = Medoc
    form_class = AjoutProduit
    template_name = "Medicaments/ajout-donnees.html"
    success_url = reverse_lazy("home")


# -----------------------------
# MODIFICATION PRODUIT
# -----------------------------
class UpdateDonnees(LoginRequiredMixin, UpdateView):
    model = Medoc
    form_class = AjoutProduit
    template_name = "Medicaments/modification.html"
    success_url = reverse_lazy("home")


# -----------------------------
# SUPPRESSION PRODUIT
# -----------------------------
class DeleteDonnees(LoginRequiredMixin, DeleteView):
    model = Medoc
    template_name = "Medicaments/delete.html"
    success_url = reverse_lazy("home")


class edit(LoginRequiredMixin, DetailView):

    model = Medoc
    template_name = 'Medicaments/detail.html'
    context_object_name = 'n'



# -----------------------------
# RECHERCHE PRODUIT
# -----------------------------
@login_required(login_url="login")
def recherche(request):
    query = request.GET.get("produit", "").strip()

    # ✅ Si champ vide : on retourne la liste complète
    if query == "":
        donnees = Medoc.objects.all()
    else:
        donnees = Medoc.objects.filter(name__icontains=query)

    return render(request, "Medicaments/resultat_recheche.html", {
        "donnees": donnees,
        "query": query
    })
# fonction pour la vente

def VenteProduits(request, id):
    medoc = get_object_or_404(Medoc, id=id)
    message = None

    if request.method == 'POST':
        form = AjoutVente(request.POST)
        if form.is_valid():
            quantite = form.cleaned_data['quantite']
            customer_name = form.cleaned_data['customer']

            if quantite > medoc.quantite:
                message = "La quantité demandée dépasse le stock disponible !"
            else:
                customer, _ = Customer.objects.get_or_create(name=customer_name)

                total_amount = Decimal(medoc.price) * Decimal(quantite)

                sale = Vente.objects.create(
                    medoc=medoc,
                    quantite=quantite,
                    total_amount=total_amount,
                    customer=customer
                )

                medoc.quantite -= quantite
                medoc.save()

                return redirect('facture', sale_id=sale.id)
    else:
        form = AjoutVente()

    if medoc.quantite <= 5 and not message:
        message = "Attention, le stock est bas !"

    return render(request, 'Medicaments/formulaire_vente.html', {
        'produit': medoc,
        'form': form,
        'message': message
    })

def SaveRecu(request, id):

    vente = get_object_or_404(Vente, id=id)
    customer = vente.customer
    quantite = vente.quantite
    total_amount = vente.total_amount
    produit = vente.produit

    recu = Facture_Client(
        customer = customer,
        quantite = quantite,
        total_amount = total_amount,
        produit = produit
    )

    recu.save()

    return redirect('facture', sale_id = id)


#  fonction pour afficher les données de la vente

def Facture(request, sale_id):

    sale = get_object_or_404(Vente, id=sale_id)
    
    customer = sale.customer
    produit = sale.medoc        # ✅ on récupère le medoc vendu
    quantite = sale.quantite
    sale_date = sale.sale_date
    total_amount = sale.total_amount

    context = {
        'sale': sale,
        'customer': customer,
        'produit': produit,          # ✅ variable bien définie
        'quantite': quantite,
        'sale_date': sale_date,
        'id': sale.id,
        'prix_unitaire': produit.price,   # ✅ accès correct
        'total_amount': total_amount ,
        # ✅ Infos “ticket” (tu peux les rendre dynamiques plus tard)
        "pharmacie_nom": "SO MAI SONKA",
        "pharmacie_adresse": "ADRESSE ICI ",
        "pharmacie_ville": "DIFFA",
        "pharmacie_tel": "+227 XX XX XX XX",
        "pharmacie_nif": "35291/S",
        "pharmacie_rccm": "RCCM-NE-DIF-2025-A-242",
        "vendeur": request.user.username,   # ou un champ “vendeur” si tu veux
        "caissier": request.user.username,  # idem
        "mode_paiement": "Espèce",
    }

    return render(request, 'Medicaments/facture_client.html', context)

class vente(ListView):
    template_name = 'Medicaments/vente.html'
    queryset = Vente.objects.all()

def recu(request):
    recus = Facture_client.objects.all()
    
    return render (request, 'Medicaments/recu.html',{'recus': recus})

#historique des ventes
@login_required(login_url="login")
def historique_ventes(request):
    q = request.GET.get("q", "").strip()

    ventes = Vente.objects.select_related("medoc", "customer").order_by("-sale_date")

    if q:
        ventes = ventes.filter(
            Q(medoc__name__icontains=q) |
            Q(customer__name__icontains=q)
        )

    context = {
        "ventes": ventes,
        "q": q,
    }
    return render(request, "Medicaments/historique_ventes.html", context)