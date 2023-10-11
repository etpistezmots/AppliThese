from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect
# Create your views here.

def home(request):
    return render(request,'Introduction/home.html')


def VersTheseMBeligne(request):
    return render(request, 'Introduction/TheseMBeligne.html')




