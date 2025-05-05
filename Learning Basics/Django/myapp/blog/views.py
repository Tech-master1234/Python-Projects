from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.urls import reverse
import logging
from .models import Post
# Create your views here.
# posts = [
#     {'id':1,'title':'Post 1','content':'Content of post 1'},
#     {'id':2,'title':'Post 2','content':'Content of post 2'},
#     {'id':3,'title':'Post 3','content':'Content of post 3'},
#     {'id':4,'title':'Post 4','content':'Content of post 4'},
# ]
blog_title = 'Todays picks'
site_title = 'Blog Posts'

def index(requests):
    posts = Post.objects.all()
    return render(requests,'index.html',{'blog_title':blog_title,'site_title' : site_title,'posts':posts})

def detail(requests,post_id):
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        raise Http404("Post Does Not Exist!")
    return render(requests,'detail.html',{'post':post})

def old_url_redirect(requests):
    return redirect(reverse('blog:new_page_url'))

def new_url_view(requests):
    return HttpResponse("This is new URL")
