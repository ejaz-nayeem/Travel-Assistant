from django.contrib import admin
from .models import LegalPage

@admin.register(LegalPage)
class LegalPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'last_updated')
    # This automatically creates the slug from the title, which is very helpful.
    prepopulated_fields = {'slug': ('title',)}
