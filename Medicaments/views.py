from django.shortcuts import render, get_object_or_404, redirect
from decimal import Decimal
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_POST
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.db.models import Q
from django.contrib import messages
from django.http import HttpResponseRedirect
from datetime import timedelta
from django.db.models import Sum
from django.db.models.functions import TruncDate

from .models import Medoc, Customer, Vente, Facture_client, Panier, LignePanier
from .forms import AjoutProduit, AjoutVente


# -----------------------------
# LISTE / AFFICHAGE DES PRODUITS
# -----------------------------
class Affichage(LoginRequiredMixin, ListView):
    model = Medoc
    template_name = "Medicaments/home.html"
    queryset = Medoc.objects.filter(is_active=True)  # ✅ n'affiche plus les produits archivés
    context_object_name = "donnees"


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
# SUPPRESSION PRODUIT (SOLUTION 3 = ARCHIVAGE)
# -----------------------------
class DeleteDonnees(LoginRequiredMixin, DeleteView):
    model = Medoc
    template_name = "Medicaments/delete.html"
    success_url = reverse_lazy("home")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        # ✅ Soft delete : on archive au lieu de supprimer (évite ProtectedError)
        self.object.is_active = False
        self.object.save(update_fields=["is_active"])

        messages.success(request, f"Produit '{self.object.name}' archivé avec succès ✅")
        return redirect(self.success_url)


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

    base_qs = Medoc.objects.filter(is_active=True)

    if query == "":
        donnees = base_qs
    else:
        donnees = base_qs.filter(name__icontains=query)

    return render(request, "Medicaments/resultat_recheche.html", {
        "donnees": donnees,
        "query": query
    })


# -----------------------------
# VENTE SIMPLE (ton existant)
# -----------------------------
def VenteProduits(request, id):
    medoc = get_object_or_404(Medoc, id=id, is_active=True)
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

    Facture_client.objects.create(
        customer=vente.customer,
        quantite=vente.quantite,
        vente=vente,
        medoc=vente.medoc,
    )

    return redirect('facture', sale_id=vente.id)


def Facture(request, sale_id):
    # Vente "référence" (la dernière vente créée)
    sale = get_object_or_404(Vente, id=sale_id)
    customer = sale.customer

    # ✅ regroupe les ventes du panier faites dans la même fenêtre de temps
    t = sale.sale_date
    start = t - timedelta(seconds=3)
    end = t + timedelta(seconds=3)

    ventes = (
        Vente.objects
        .filter(customer=customer, sale_date__range=(start, end))
        .select_related("medoc")
        .order_by("id")
    )

    lignes = []
    total_amount = Decimal("0.00")

    for v in ventes:
        pu = v.medoc.price
        montant = Decimal(pu) * Decimal(v.quantite)
        total_amount += montant
        lignes.append({
            "produit": v.medoc,
            "quantite": v.quantite,
            "prix_unitaire": pu,
            "montant": montant,
        })

    context = {
        "sale": sale,
        "customer": customer,
        "sale_date": sale.sale_date,
        "id": sale.id,

        "lignes": lignes,
        "total_amount": total_amount,

        "pharmacie_nom": "SO MAI SONKA",
        "pharmacie_adresse": "ADRESSE ICI ",
        "pharmacie_ville": "DIFFA",
        "pharmacie_tel": "+227 XX XX XX XX",
        "pharmacie_nif": "35291/S",
        "pharmacie_rccm": "RCCM-NE-DIF-2025-A-242",
        "vendeur": request.user.username,
        "caissier": request.user.username,
        "mode_paiement": "Espèce",
    }

    return render(request, "Medicaments/facture_client.html", context)


class vente(ListView):
    template_name = 'Medicaments/vente.html'
    queryset = Vente.objects.all()


def recu(request):
    recus = Facture_client.objects.all()
    return render(request, 'Medicaments/recu.html', {'recus': recus})


@login_required(login_url="login")
def historique_ventes(request):
    q = request.GET.get("q", "").strip()

    ventes = Vente.objects.select_related("medoc", "customer").order_by("-sale_date")

    if q:
        ventes = ventes.filter(
            Q(medoc__name__icontains=q) |
            Q(customer__name__icontains=q)
        )

    return render(request, "Medicaments/historique_ventes.html", {
        "ventes": ventes,
        "q": q,
    })


# ==========================================================
# ✅ PANIER : ajout + update qté + valider
# ==========================================================

@login_required(login_url="login")
def panier_view(request):
    panier, _ = Panier.objects.get_or_create(user=request.user, is_active=True)
    lignes = panier.lignes.select_related("medoc").all()

    total_panier = sum((l.prix_unitaire * l.quantite for l in lignes), Decimal("0.00"))
    insuffisant = any(l.quantite > l.medoc.quantite for l in lignes)

    return render(request, "Medicaments/panier.html", {
        "panier": panier,
        "lignes": lignes,
        "total_panier": total_panier,
        "insuffisant": insuffisant,
    })


@login_required(login_url="login")
def ajouter_au_panier(request, medoc_id):
    # ✅ interdit ajout si produit archivé
    medoc = get_object_or_404(Medoc, id=medoc_id, is_active=True)
    panier, _ = Panier.objects.get_or_create(user=request.user, is_active=True)

    ligne, _ = LignePanier.objects.get_or_create(
        panier=panier,
        medoc=medoc,
        defaults={"quantite": 0, "prix_unitaire": medoc.price}
    )

    ligne.prix_unitaire = medoc.price
    ligne.quantite += 1
    ligne.save()

    messages.success(request, f"{medoc.name} ajouté au panier ✅")
    return HttpResponseRedirect(request.META.get("HTTP_REFERER", reverse("home")))


@login_required(login_url="login")
@require_POST
def update_panier(request):
    panier, _ = Panier.objects.get_or_create(user=request.user, is_active=True)
    lignes = panier.lignes.select_related("medoc").all()

    for l in lignes:
        key = f"qte_{l.id}"
        if key in request.POST:
            try:
                qte = int(request.POST.get(key, l.quantite))
            except ValueError:
                qte = l.quantite

            if qte <= 0:
                l.delete()
                continue

            stock = l.medoc.quantite
            if qte > stock:
                l.quantite = stock
                l.save()
                messages.error(
                    request,
                    f"Stock insuffisant pour {l.medoc.name}. Stock dispo: {stock}. Quantité ajustée."
                )
            else:
                l.quantite = qte
                l.prix_unitaire = l.medoc.price
                l.save()

    return redirect("panier")


@login_required(login_url="login")
def supprimer_ligne_panier(request, ligne_id):
    panier, _ = Panier.objects.get_or_create(user=request.user, is_active=True)
    LignePanier.objects.filter(id=ligne_id, panier=panier).delete()
    return redirect("panier")


@login_required(login_url="login")
def checkout_panier(request):
    panier, _ = Panier.objects.get_or_create(user=request.user, is_active=True)
    lignes = panier.lignes.select_related("medoc").all()

    if not lignes.exists():
        messages.warning(request, "Panier vide.")
        return redirect("panier")

    for l in lignes:
        if l.quantite > l.medoc.quantite:
            messages.error(
                request,
                f"Stock insuffisant pour {l.medoc.name} (dispo: {l.medoc.quantite}). Corrige le panier."
            )
            return redirect("panier")

    total_panier = sum((l.prix_unitaire * l.quantite for l in lignes), Decimal("0.00"))

    return render(request, "Medicaments/checkout.html", {
        "panier": panier,
        "lignes": lignes,
        "total_panier": total_panier,
    })


@login_required(login_url="login")
@require_POST
def valider_panier(request):
    panier, _ = Panier.objects.get_or_create(user=request.user, is_active=True)
    lignes = panier.lignes.select_related("medoc").all()

    if not lignes.exists():
        messages.warning(request, "Panier vide.")
        return redirect("panier")

    customer_name = request.POST.get("customer", "").strip()
    mode_paiement = request.POST.get("mode_paiement", "Espèce").strip() or "Espèce"

    if not customer_name:
        messages.error(request, "Veuillez saisir le nom du client.")
        return redirect("checkout_panier")

    customer, _ = Customer.objects.get_or_create(name=customer_name)

    for l in lignes:
        if l.quantite > l.medoc.quantite:
            messages.error(request, f"Stock insuffisant pour {l.medoc.name} (dispo: {l.medoc.quantite}).")
            return redirect("panier")

    last_sale_id = None

    for l in lignes:
        total_amount = Decimal(l.prix_unitaire) * Decimal(l.quantite)

        sale = Vente.objects.create(
            medoc=l.medoc,
            quantite=l.quantite,
            customer=customer,
            total_amount=total_amount
        )
        last_sale_id = sale.id

        l.medoc.quantite -= l.quantite
        l.medoc.save()

        Facture_client.objects.create(
            customer=customer,
            quantite=l.quantite,
            vente=sale,
            medoc=l.medoc,
        )

    panier.is_active = False
    panier.save()

    messages.success(request, "Vente validée ✅")
    return redirect("facture", sale_id=last_sale_id)


@login_required(login_url="login")
def vider_panier(request):
    panier = Panier.objects.filter(user=request.user, is_active=True).first()
    if panier:
        panier.lignes.all().delete()
        messages.success(request, "Panier vidé avec succès 🗑️")
    return redirect("panier")


# -----------------------------
# DASHBOARD
# -----------------------------
@login_required(login_url="login")
def dashboard(request):
    date_debut = request.GET.get("date_debut")
    date_fin = request.GET.get("date_fin")

    ventes = Vente.objects.all()

    if date_debut and date_fin:
        ventes = ventes.filter(sale_date__date__range=[date_debut, date_fin])

    total_ca = ventes.aggregate(Sum("total_amount"))["total_amount__sum"] or 0
    total_quantite = ventes.aggregate(Sum("quantite"))["quantite__sum"] or 0
    total_ventes = ventes.count()

    panier_moyen = 0
    if total_ventes > 0:
        panier_moyen = total_ca / total_ventes

    top_produits = (
        ventes.values("medoc__name")
        .annotate(total_vendu=Sum("quantite"))
        .order_by("-total_vendu")[:5]
    )

    stock_critique = Medoc.objects.filter(is_active=True, quantite__lte=5)

    ventes_par_jour = (
        ventes
        .annotate(jour=TruncDate("sale_date"))
        .values("jour")
        .annotate(total=Sum("total_amount"))
        .order_by("jour")
    )

    context = {
        "total_ca": total_ca,
        "total_quantite": total_quantite,
        "total_ventes": total_ventes,
        "panier_moyen": panier_moyen,
        "top_produits": top_produits,
        "stock_critique": stock_critique,
        "ventes_par_jour": list(ventes_par_jour),
    }

    return render(request, "Medicaments/dashboard.html", context)
