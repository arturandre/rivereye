from django.shortcuts import render


# Create your views here.

def Home(request):
    return render(request,'home.html')

def Home2(request):
    return render(request,'pagina/index.html')