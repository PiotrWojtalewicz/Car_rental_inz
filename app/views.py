from django.http import HttpResponse

def home(request):
    return HttpResponse("Witaj w naszej wypożyczalni samochodów!")
