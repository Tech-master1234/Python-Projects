from typing import Any
from blog.models import Post, Category
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "This commands inserts post data"

    def handle(self, *args: Any, **options: Any):
        # Deleting Existing data
        Category.objects.all().delete()

        categories = ["Sports","Technology", "Food", "Science", "Art"]
        for category_name in categories:
                    Category.objects.create(name = category_name)

        self.stdout.write(self.style.SUCCESS("Completed inserting Data!"))