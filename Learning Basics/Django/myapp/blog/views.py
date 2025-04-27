from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse

# Create your views here.

def index(requests):
    return HttpResponse("At Blog's Home Page")

def detail(requests,post_id):
    return HttpResponse(f"At details Page {post_id}")

def old_url_redirect(requests):
    return redirect(reverse('blog:new_page_url_something'))

def new_url_view(requests):
    return HttpResponse("This is new URL")
