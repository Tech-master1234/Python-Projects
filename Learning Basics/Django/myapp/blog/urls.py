from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name = "index"),
    path("post/details/<str:post_id>", views.detail, name="detail")
    # path("post/details/<int:post_id>", views.detail, name="detail")

]