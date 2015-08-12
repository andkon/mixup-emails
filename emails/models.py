from django.db import models
from django.contrib.auth.models import User
from emails.colourfield import ColourField

# Create your models here.

def upload_pic_to(instance, filename):
	import os
	from django.utils.timezone import now

	instance_name = instance.__class__.__name__
	if instance_name is Emoji.__name__:
		directory = "emoji"

	filename_base, filename_ext = os.path.splitext(filename)
	return '%s/%s%s' % (
		directory,
		now().strftime("%Y%m%d%H%M%S"),
		filename_ext.lower(),
	)

class EmojiSet(models.Model):
	emojis = models.ManyToManyField('Emoji', related_name='in_sets', through='SettedEmoji')
	name = models.CharField(max_length=50)

	def __unicode__(self):
		return "%s Emoji Set - contains %s emoji" % (self.name, self.emojis.count())

class SettedEmoji(models.Model):
	emoji = models.ForeignKey('Emoji', related_name='emoji_for_sets')
	emoji_set = models.ForeignKey('EmojiSet', related_name='emoji_in_set')
	position = models.IntegerField(max_length=2)
	color = ColourField(blank=True, null=True)

	class Meta:
		unique_together = ('position', 'emoji',)

class Playlist(models.Model):
	SERVICES = (
		("SZA", 'Songza'),
		('SFY', 'Spotify'),
		('RDO', 'Rdio'),
		('8KS', '8tracks'),
		('NPC', 'Noon Pacific'),
		('BOP', 'Bop.fm'),
		('GSK', 'Grooveshark'),
		('HPM', 'Hype Machine'),
	)

	url = models.URLField(max_length=200)
	title = models.CharField(max_length=200)
	description = models.CharField(max_length=300, blank=True, null=True)
	genre = models.CharField(max_length=50, blank=True, null=True)
	# rank from 1-5
	ranking = models.PositiveIntegerField(max_length=1, blank=True, null=True)
	service = models.CharField(max_length=3, choices=SERVICES)

	class Meta:
		verbose_name = "Playlist"
		verbose_name_plural = "Playlists"

	def __unicode__(self):
		return "%s from %s" % (self.title, self.get_service_display())

class NewsletterPlaylist(models.Model):
	playlist = models.ForeignKey(Playlist, related_name='newsletter_playlist')
	newsletter = models.ForeignKey('Newsletter', related_name='playlists_through')
	position = models.IntegerField(max_length=2)
	alt_emoji = models.ForeignKey('Emoji', related_name='alt_for_newsletter_playlists', null=True, blank=True)

	def get_emoji_url(self):
		return self.newsletter.emoji_set.emojis.get(emoji_for_sets__position=self.position).image.url

	emoji_url = property(get_emoji_url)

	def __unicode__(self):
		return "'%s' in newsletter %s" % (self.playlist.title, self.newsletter.pk)

class Emoji(models.Model):
	emoji = models.CharField(max_length=2, primary_key=True)
	image = models.ImageField(blank=True, null=True, upload_to=upload_pic_to)
	created = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ('-created',)

	def __unicode__ (self):
		return "%s" % (self.emoji)
	
class EmailProfile(models.Model):
	SOURCES = (
		("FRD", "Friend signed you up."),
		("NU", "'Not you' button in e-mail."),
		("HPG", "Homepage."),
	)
	joined = models.DateTimeField(auto_now_add=True)
	email = models.EmailField(primary_key=True)
	signup_source = models.CharField(max_length=3, choices=SOURCES, null=True, blank=True)
	user = models.ForeignKey(User, null=True, blank=True)
	is_subscribed = models.BooleanField(default=True)
	is_confirmed = models.BooleanField(default=False)
	invited_by = models.ForeignKey('EmailProfile', null=True, blank=True)

	def __unicode__(self):
		return "%s" % (self.email)


class Newsletter(models.Model):
	send_date = models.DateTimeField(null=True, blank=True)
	emoji_set = models.ForeignKey(EmojiSet, related_name='used_in_newsletters', blank=True, null=True)
	sent_to = models.ManyToManyField(EmailProfile, related_name='received_newsletters', blank=True, null=True)
	playlists = models.ManyToManyField(Playlist, related_name='in_newsletters', through=NewsletterPlaylist, blank=True, null=True)
	message = models.CharField(max_length=1000, null=True, blank=True)
	subject = models.CharField(max_length=140, null=True, blank=True)
	send_task = models.CharField(max_length=200, null=True, blank=True)

	def __unicode__(self):
		return "Edition %s" % (self.pk)

class PlaylistClick(models.Model):
	clicked_playlist = models.ForeignKey(Playlist, related_name='clicks')
	clicked_by = models.ForeignKey(EmailProfile, related_name='clicked_on', blank=True, null=True)
	newsletter = models.ForeignKey(Newsletter, related_name='clicks', blank=True, null=True)
	clicked_on = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		try:
			return "%s/%s: '%s' clicked by %s" % (self.clicked_on.month, self.clicked_on.day, self.clicked_playlist.title, self.clicked_by.email)
		except AttributeError:
			return "%s/%s: '%s' clicked by no one" % (self.clicked_on.month, self.clicked_on.day, self.clicked_playlist.title)
