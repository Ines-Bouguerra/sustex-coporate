from django.http import HttpResponse

# Create your views here.
def index(request):
    return HttpResponse("<h1>Hello and welcome to my first <u>Django App</u> project!</h1>")