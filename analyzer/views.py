from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    """Página de inicio: renderiza la interfaz principal"""
    return render(request, 'analyzer/index.html')
