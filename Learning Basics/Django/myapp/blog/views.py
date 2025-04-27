from django.shortcuts import render, redirect
from django.http import HttpResponse

# Create your views here.

def index(requests):
    return HttpResponse("At Blog's Home Page")

def detail(requests,post_id):
    return HttpResponse(f"At details Page {post_id}")

def old_url_redirect(requests):
    return redirect('new_url')

def new_url_view(requests):
    return HttpResponse("This is new URL")
