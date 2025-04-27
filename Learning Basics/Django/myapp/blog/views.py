from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse

# Create your views here.

def index(requests):
    return render(requests,'index.html')

def detail(requests,post_id):
    return render(requests,'detail.html')

def old_url_redirect(requests):
    return redirect(reverse('blog:new_page_url'))

def new_url_view(requests):
    return HttpResponse("This is new URL")
