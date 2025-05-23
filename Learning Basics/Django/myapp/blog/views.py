from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.urls import reverse
import logging
from .models import Post
from .forms import ContactForm
from django.core.paginator import Paginator
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

    # Get the posts from DB
    all_posts = Post.objects.all()

    # Pagination
    paginator = Paginator(all_posts, 5)
    page_number = requests.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(requests,'index.html',{'blog_title':blog_title,'site_title' : site_title,'page_obj':page_obj})

def detail(requests,slug):
    try:
        post = Post.objects.get(slug=slug)
        related_posts = Post.objects.filter(category = post.category).exclude(pk=post.id)
    except Post.DoesNotExist:
        raise Http404("Post Does Not Exist!")
    return render(requests,'detail.html',{'post':post, 'related_posts':related_posts})


def contact_view(requests):
    if requests.method == 'POST':
        form = ContactForm(requests.POST)
        name = requests.POST.get('name')
        email = requests.POST.get('email')
        message = requests.POST.get('message')
        logger = logging.getLogger()
        if form.is_valid():
            logger.debug(f'POST Data is {form.cleaned_data['name']},{form.cleaned_data['email']},{form.cleaned_data['message']}')
            success_message = "Your message has been sent successfully"
            return render(requests,'contact.html',{'blog_title':blog_title,'site_title' : site_title,'success_message':success_message})
        else:
            logger.debug("Form validation failed")
        return render(requests,'contact.html',{'blog_title':blog_title,'site_title' : site_title,'form':form,'name':name,'email':email,'message':message})
    return render(requests,'contact.html',{'blog_title':blog_title,'site_title' : site_title})


def about_page(requests):
    return render(requests,'about.html',{'blog_title':blog_title,'site_title' : site_title})

