from django.shortcuts import render
from django.contrib.auth.models import User


def home(request):
    return render(request, 'general/home.html')


def useplus(request):
    return render(request, 'general/useplus.html')


# Malheureusement, pas directement accessible dans l'admin !
def getiduser(request):
    listusers = User.objects.all()
    context = {"listusers":listusers}
    return render(request, 'general/getiduser.html',context)