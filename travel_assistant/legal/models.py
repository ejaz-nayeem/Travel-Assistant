from django.db import models

class LegalPage(models.Model):
    title = models.CharField(max_length=100, unique=True)
    # A slug is a URL-friendly version of the title, e.g., "terms-and-conditions"
    slug = models.SlugField(max_length=100, unique=True, help_text="A URL-friendly version of the title.")
    content = models.TextField()
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']