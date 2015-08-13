from django.contrib import admin
from emails.models import Newsletter

# Register your models here.
class NewsletterAdmin(admin.ModelAdmin):
	inlines = [NewsletterPlaylistInline]

admin.site.register(Newsletter, NewsletterAdmin)