from .models import Panier

def panier_counter(request):
    if request.user.is_authenticated:
        panier = Panier.objects.filter(user=request.user, is_active=True).first()
        if panier:
            count = panier.lignes.count()   # nb de lignes (produits différents)
        else:
            count = 0
    else:
        count = 0

    return {"panier_count": count}
