from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages

import re
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


# -----------------------------
# CRÉER UN COMPTE
# -----------------------------
def Creation_Compte(request):
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')

        # Vérification des mots de passe
        if password != password_confirm:
            messages.error(request, "Les mots de passe ne sont pas identiques. Veuillez réessayer.")
            return redirect("creation")

        # Vérification longueur + complexité
        if (
            len(password) < 8
            or not re.search(r'[A-Za-z]', password)
            or not re.search(r'\d', password)
            or not re.search(r'[!@#$%(),.?":{}`|<>]', password)
        ):
            messages.error(
                request,
                "Le mot de passe doit contenir au moins 8 caractères, incluant des lettres, des chiffres et des caractères spéciaux."
            )
            return redirect("creation")

        # Vérification format e-mail
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Adresse e-mail invalide. Veuillez réessayer.")
            return redirect("creation")

        # Vérification existence user/email
        if User.objects.filter(username=username).exists():
            messages.error(request, "Ce nom d'utilisateur existe déjà. Veuillez réessayer.")
            return redirect("creation")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Cette adresse e-mail est déjà utilisée. Veuillez en choisir une autre.")
            return redirect("creation")

        # Création user
        User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, "Compte créé avec succès. Connectez-vous maintenant.")
        return redirect("login")

    return render(request, "creation.html")


# -----------------------------
# SE CONNECTER
# -----------------------------
def Connecter_Compte(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username = username, password = password)

        if user is not None:
            login(request, user)
            return redirect('acc')
        
        else:
            messages.error(request, "Nom d'utilisateur ou le mot de passe incorect.")
            return redirect("login")
    return render (request, 'login.html')

# -----------------------------
# VÉRIFICATION E-MAIL (mot de passe oublié)
# -----------------------------
def Verification_Mail(request):
    if request.method == "POST":
        email = request.POST.get('email', '').strip()

        if not email:
            messages.error(request, "Veuillez rentrer une adresse mail valide.")
            return render(request, "verificaionMail.html")

        # ✅ .first() corrigé
        user = User.objects.filter(email=email).first()

        if user:
            return redirect("modifierCode", email=email)

        messages.error(
            request,
            "Cette adresse ne correspond à aucun compte. Veuillez réessayer avec une autre ou créez un compte."
        )
        return redirect("verification")

    return render(request, "verificaionMail.html")


# -----------------------------
# CHANGER MOT DE PASSE
# -----------------------------
def Changement_Code(request, email):
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        messages.error(request, "Utilisateur introuvable.")
        return redirect("verification")

    if request.method == "POST":
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')

        if password != password_confirm:
            messages.error(request, "Les mots de passe ne correspondent pas. Réessayez.")
            return redirect("modifierCode", email=email)

        if len(password) < 8:
            messages.error(request, "Le mot de passe doit contenir au moins 8 caractères.")
            return redirect("modifierCode", email=email)

        if not any(char.isdigit() for char in password):
            messages.error(request, "Le mot de passe doit contenir au moins un chiffre.")
            return redirect("modifierCode", email=email)

        if not any(char.isalpha() for char in password):
            messages.error(request, "Le mot de passe doit contenir au moins une lettre.")
            return redirect("modifierCode", email=email)

        user.set_password(password)
        user.save()
        messages.success(request, "Mot de passe modifié. Connectez-vous maintenant.")
        return redirect("login")

    return render(request, "nouveauMDP.html", {"email": email})


# -----------------------------
# DÉCONNEXION
# -----------------------------
def Deconnection(request):
    logout(request)
    return redirect("login")
