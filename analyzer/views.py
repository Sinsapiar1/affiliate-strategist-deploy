from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    """Vista básica para la página de inicio"""
    return HttpResponse("¡Affiliate Strategist funcionando en Railway!")
