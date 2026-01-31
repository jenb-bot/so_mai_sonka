from django.db import models
from django.conf import settings

class Categories(models.Model):
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name


class Medoc(models.Model):
    name = models.CharField(max_length=100)  # ✅ plus de virgule
    category = models.ForeignKey(Categories, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantite = models.PositiveBigIntegerField(default=0)
    description = models.TextField()
    date_ajout = models.DateField(auto_now_add=True)
    date_expiration = models.DateField()
    img = models.ImageField(null=True, blank=True, upload_to='media/')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-date_ajout']

    def statut_quantite(self):
        if self.quantite <= 5:
            return 'red'
        elif self.quantite <= 20:
            return 'orange'
        return 'green'

    def __str__(self):
        return self.name




class Customer(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    

class Vente(models.Model):
    medoc = models.ForeignKey(Medoc, on_delete=models.CASCADE)
    sale_date = models.DateTimeField(auto_now_add=True)
    quantite = models.PositiveIntegerField()
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)  # ✅ FK au lieu de CharField
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Vente - {self.medoc.name} ({self.quantite})"


class Facture_client(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField()
    date_achat = models.DateTimeField(auto_now_add=True)  # ✅ évite l'erreur si tu ne passes pas la date
    vente = models.ForeignKey(Vente, on_delete=models.CASCADE)
    medoc = models.ForeignKey(Medoc, on_delete=models.CASCADE)

    def __str__(self):
        return f"Reçu - {self.customer.name} / {self.medoc.name}"

class Panier(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Panier #{self.id} - {self.user}"


class LignePanier(models.Model):
    panier = models.ForeignKey(Panier, on_delete=models.CASCADE, related_name="lignes")
    medoc = models.ForeignKey(Medoc, on_delete=models.PROTECT)
    quantite = models.PositiveIntegerField(default=1)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def total_ligne(self):
        return self.prix_unitaire * self.quantite

    def __str__(self):
        return f"{self.medoc.name} x{self.quantite}"


