from django.contrib import admin
from emails.models import Playlist, Newsletter, NewsletterPlaylist, Emoji, SettedEmoji

# Register your models here.
class NewsletterPlaylistInline(admin.TabularInline):
	model = NewsletterPlaylist

class EmojiAdmin(admin.ModelAdmin):
	pass

class SettedEmojiAdmin(admin.ModelAdmin):
	pass

class PlaylistAdmin(admin.ModelAdmin):
	inlines = [NewsletterPlaylistInline]

class NewsletterAdmin(admin.ModelAdmin):
	inlines = [NewsletterPlaylistInline]


admin.site.register(Playlist, PlaylistAdmin)
admin.site.register(Emoji)
admin.site.register(SettedEmoji)
admin.site.register(Newsletter, NewsletterAdmin)