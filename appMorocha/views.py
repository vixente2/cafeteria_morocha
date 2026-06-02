from django.shortcuts import render
from django.http import HttpResponse
from .db import ConexionDB
# Create your views here.
def inicio(request):
    return render(request,'appMorocha/inicio.html')

def login(request):
    return render(request,'appMorocha/login.html')

def registrarPedido(request):
    return render(request,'appMorocha/registrarPedido.html')