from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def index(requests):
    return HttpResponse("At Blog's Home Page")

def detail(requests,post_id):
    return HttpResponse(f"At details Page {post_id}")
