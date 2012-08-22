
from django.http import HttpResponse


def index(request):
    return HttpResponse('Index Page')


def detail(request, rss_name):
    return HttpResponse(rss_name + ' rss feed.')
