from django.contrib import admin

# Register your models here.

from .models import Post,Category


class PostAdmin(admin.ModelAdmin):
    list_display = ('title','content')
    search_fields = ('title','content')
    list_filter = ('category','created_at')
admin.site.register(Post,PostAdmin)
admin.site.register(Category)