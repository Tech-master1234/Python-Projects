from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path("", views.index, name = "index"),
    path("post/details/<str:slug>", views.detail, name="detail"),
    path("contact", views.contact_view, name='contact'),
    path("about", views.about_page, name='about')

]