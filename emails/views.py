from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import View
from django.views.generic.base import RedirectView, TemplateView, TemplateResponseMixin
from django.db import IntegrityError

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, user_passes_test

from emails.models import *
from emails.forms import *
from django.forms.formsets import formset_factory
from emails.tokens import default_token_generator

import sys

from emails.tasks import send_newsletter, send_confirmation_emails, send_latest_newsletter_to_emails, send_to_andrew
from celery import shared_task

import datetime
import pytz
from django.core import mail
from django.template import Context, loader

"""
ARCHIVED PLAYLIST VIEWS
"""

class NewsletterView(TemplateView):
	template_name = "emails/hero_preprocessed.html"

	def get_context_data(self, **kwargs):
		context = super(NewsletterView, self).get_context_data(**kwargs)
		newsletter_id = self.kwargs['newsletter_id']
		newsletter = Newsletter.objects.get(pk=newsletter_id)
		context['newsletter'] = newsletter
		context['playlists'] = newsletter.playlists_through.all().order_by('-position')
		return context

class LatestNewsletter(TemplateView):
	template_name = "emails/hero_preprocessed.html"

	def get_context_data(self, **kwargs):
		context = super(LatestNewsletter, self).get_context_data(**kwargs)
		newsletter = Newsletter.objects.filter(send_date__isnull=False).order_by('-send_date')[0]
		context['newsletter'] = newsletter
		context['playlists'] = newsletter.playlists_through.all().order_by('-position')
		return context

class NewsletterEmailView(TemplateView):
	template_name = "emails/hero_preprocessed.html"
	# How to make these template views: http://stackoverflow.com/questions/15754122/url-parameters-and-logic-in-django-class-based-views-templateview

	def get_context_data(self, **kwargs):
		# Gets the context from the current request.
		context = super(NewsletterEmailView, self).get_context_data(**kwargs)
		
		# Gets the url parameters:
		newsletter_id = self.kwargs['newsletter_id']
		email = self.kwargs['email']

		newsletter = Newsletter.objects.get(pk=newsletter_id)
		context['newsletter'] = newsletter
		context['playlists'] = newsletter.playlists_through.all().order_by('-position')
		context['email_profile'] = EmailProfile.objects.get(pk=email)
		return context
		

class PlaylistEmailRedirect(View):
	def get(self, request, newsletter_id, playlist_pk, email):
		"""
		ALRIGHT ALRIGHT ALRIGHT
		This creates a PlaylistClick object for a given EmailProfile or User
		Then redirects the user to the playlist url
		"""
		playlist = get_object_or_404(Playlist, pk=playlist_pk)
		email = get_object_or_404(EmailProfile, pk=email)
		newsletter = get_object_or_404(Newsletter, pk=newsletter_id)
		PlaylistClick.objects.create(clicked_playlist=playlist, clicked_by=email, newsletter=newsletter)
		return HttpResponseRedirect(playlist.url)

class PlaylistRedirect(View):
	def get(self, request, newsletter_id, playlist_pk):
		"""
		ALRIGHT ALRIGHT ALRIGHT
		This creates a PlaylistClick object for a given EmailProfile or User
		Then redirects the user to the playlist url
		"""
		playlist = get_object_or_404(Playlist, pk=playlist_pk)
		newsletter = get_object_or_404(Newsletter, pk=newsletter_id)
		PlaylistClick.objects.create(clicked_playlist=playlist, newsletter=newsletter)
		return HttpResponseRedirect(playlist.url)


"""
SUBSCRIBING, CONFIRMING, UNSUBSCRIBING, AND ADDING FRIENDS
"""


class Subscribe(View):
	def get(self, request):
		form = EmailSubscribeForm()
		return render(request, 'subscribe.html', {'form': form})

	def post(self, request):
		form = EmailSubscribeForm(request.POST)
		if form.is_valid():
			# Time to create the object then send them the 'did subscribe' template
			try:
				email = self.request.POST['email']
			except KeyError:
				# handle an error saying you didn't put in an email
				error = "not_email"
				return render(request, 'after_subscribe.html', {'error':error})
			try:
				email_profile = EmailProfile.objects.create(email=email)				
			except IntegrityError:
				error = "already_sub"
				return render(request, 'after_subscribe.html', {'error':error})

			"""
			Left to do:
			+1. create send_confirmation_emails in tasks.py
			+1a) reuse the hero_preprocessed.html template to create a confirmation view
			+2. Generate the token in send_confirmation_emails
			+3. Import the token generator in ConfirmSubscription view, call default_token_generator(check_token)
			+4. If True, then in ConfirmSubscription.get, set email_profile.is_confirmed to true, show confirmed_subscribe.html
			+5. If False, then return an error to confirmed_subscribe.html just like I'm doing right below this

			
			+Then check that gmail actually is in good shape.
			+Then fill in the remaining links (for subscribe)
			+Then make the homepage view
			Then handle the invitefriends view
			Before sending:
			change subject in send_newsletter... or is it a model object?
			+make twitter,
			facebook
			remove sendgrid clicktracking
			add your own clicktracking
			profit???
			"""
			# Now start the celery task:
			res = send_confirmation_emails.delay([email_profile.email])

			return render(request, 'after_subscribe.html', {'email_profile':email_profile})
		else:
			# This'll show the errors in a list:
			return render(request, 'after_subscribe.html', {'error':form})

class ResendConfirmation(View):
	def get(self, request, email):
		try:
			email_profile = EmailProfile.objects.get(email=email)
		except EmailProfile.DoesNotExist:
			email_profile = EmailProfile.objects.create(email=email)
		res = send_confirmation_emails.delay([email_profile.email])

		return render(request, 'after_subscribe.html', {'email_profile':email_profile})

class ConfirmSubscription(View):
	def get(self, request, email, confirmation_hash):
		try:
			email_profile = EmailProfile.objects.get(email=email)
		except EmailProfile.DoesNotExist:
			email_profile = None
		
		if email_profile is not None:
			if default_token_generator.check_token(email_profile, confirmation_hash):
				email_profile.is_confirmed = True
				email_profile.is_subscribed = True
				email_profile.save()
				# Now send them the latest newsletter
				res = send_latest_newsletter_to_emails.delay([email_profile.email])
				return render(request, 'did_confirm.html', {'email_profile':email_profile, 'token':confirmation_hash})
			return render(request, 'did_confirm.html', {'token':confirmation_hash, 'email_profile':email_profile})			

		return render(request, 'did_confirm.html', {'token':confirmation_hash})


class Unsubscribe(View):
	def get(self, request, email, confirmation_hash):
		try:
			email_profile = EmailProfile.objects.get(email=email)
		except EmailProfile.DoesNotExist:
			email_profile = None
		
		if email_profile is not None:
			if default_token_generator.check_token(email_profile, confirmation_hash):
				email_profile.is_subscribed = False
				email_profile.save()
				return render(request, 'did_unsubscribe.html', {'email_profile':email_profile})
			return render(request, 'did_unsubscribe.html', {'email_profile':email_profile})			

		return render(request, 'did_confirm.html', {'token':confirmation_hash})

class InviteFriends(View):
	"""
	Use a formset to get a bunch of emails.
	"""
	def get(self, request, email):
		email_profile = get_object_or_404(EmailProfile, pk=email)
		EmailFormSet = formset_factory(EmailSubscribeForm, extra=3)
		return render(request, 'invite.html', {'email_profile': email_profile, 'formset': EmailFormSet})

	def post(self, request, email):
		EmailFormSet = formset_factory(EmailSubscribeForm)
		formset = EmailFormSet(request.POST)
		if formset.is_valid():
			print "formset is valid"
			inviter_profile = EmailProfile.objects.get(email=email)
			emails = []
			for form in formset:
				new_email = form['email'].data
				try:
					email_profile = EmailProfile.objects.create(email=new_email, invited_by=inviter_profile)
					emails.append(new_email)
				except IntegrityError:
					pass
			send_confirmation_emails.delay(emails)
			return render(request, 'after_invite.html', {'emails':emails})
		else:
			print "formset isn't valid"
			email_profile = get_object_or_404(EmailProfile, pk=email)
			return render(request, 'invite.html', {'email_profile': email_profile, 'errors':formset})

class TestTemplate(View):
	def get(self, request, subtest):
		if subtest == "confirmsubscribe":
			email_profile = EmailProfile.objects.get(email='andrew.konoff@gmail.com')
			token = default_token_generator.make_token(email_profile)
			return render(request, 'emails/confirmsubscribe.html', {'email_profile':email_profile, 'token': token})
		elif subtest == "confirmsubscribe-invited":
			email_profile = EmailProfile.objects.get(email='invited@butts.com')
			token = default_token_generator.make_token(email_profile)
			return render(request, 'emails/confirmsubscribe.html', {'email_profile':email_profile, 'token': token})
		elif subtest == "confirmsubscribe-nope":
			email_profile = EmailProfile.objects.get(email='invited@butts.com')
			token = "lololol"
			return render(request, 'emails/confirmsubscribe.html', {'email_profile':email_profile, 'token': token})



"""
SENDING PLAYLISTS
"""

def admin_check(user):
	return user.is_superuser


class SendNewsletter(View, TemplateResponseMixin):
	def get(self, request, newsletter_id):
		"""
		Populate the template, which has:
		a link to preview e-mailless newsletter message
		a link to preview newsletter message for email
		a count of users to send it to
		a link to the confirmsend view
		"""
		newsletter = get_object_or_404(Newsletter, pk=newsletter_id)

		subscriber_count = 0
		subscribers = EmailProfile.objects.filter(is_subscribed=True, is_confirmed=True)
		for email_profile in subscribers:
			# get body: https://docs.djangoproject.com/en/1.7/ref/templates/api/#module-django.template.loader
			try:
				newsletter.sent_to.get(email=email_profile.email)
			except EmailProfile.DoesNotExist:
				subscriber_count += 1

		playlists = newsletter.playlists_through.all()
		return render(request, 'sendnewsletter.html', {'newsletter': newsletter, 'user': self.request.user, 'subscribers': subscriber_count, 'playlists':playlists})


	@method_decorator(user_passes_test(admin_check))
	@method_decorator(login_required)
	def dispatch(self, *args, **kwargs):
		return super(SendNewsletter, self).dispatch(*args, **kwargs)



class ConfirmSendCelery(View, TemplateResponseMixin):
	def get(self, request, newsletter_id):
		"""
		Populate the template, which has:
		a link to preview e-mailless newsletter message
		a link to preview newsletter message for email
		a count of users to send it to
		a button to POST to this view
		"""
		newsletter = get_object_or_404(Newsletter, pk=newsletter_id)

		res = send_newsletter.delay(newsletter_id)
		newsletter.send_task = res
		newsletter.save()

		sent_to = newsletter.sent_to.all()

		return render(request, 'confirmsend.html', {'res': res, 'sent_to': sent_to, 'newsletter':newsletter})

	@method_decorator(user_passes_test(admin_check))
	@method_decorator(login_required)
	def dispatch(self, *args, **kwargs):
		return super(ConfirmSendCelery, self).dispatch(*args, **kwargs)

class TestSend(View, TemplateResponseMixin):
	def get(self, request, newsletter_id):
		"""
		Populate the template, which has:
		a link to preview e-mailless newsletter message
		a link to preview newsletter message for email
		a count of users to send it to
		a button to POST to this view
		"""
		newsletter = get_object_or_404(Newsletter, pk=newsletter_id)

		res = send_to_andrew.delay(newsletter_id)

		sent_to = EmailProfile.objects.filter(email='andrew@strings.fm')

		return render(request, 'confirmsend.html', {'res': res, 'sent_to': sent_to, 'newsletter':newsletter})

	@method_decorator(user_passes_test(admin_check))
	@method_decorator(login_required)
	def dispatch(self, *args, **kwargs):
		return super(TestSend, self).dispatch(*args, **kwargs)

class NewNewsletter(View):
	def get(self, request):
		# Just the empty form
		form = PlaylistCsvForm()
		return render(request, 'newplaylists.html', {'form': form})

	def post(self, request):
		form = PlaylistCsvForm(request.POST)
		if form.is_valid():
			# Create the playlist model objects, then preview the playlist
			csv_url = self.request.POST['url']
			newsletter_edition = self.request.POST['newsletter_edition']

			# try to get newlsetter; if not, then create it
			try:
				newsletter = Newsletter.objects.get(pk=newsletter_edition)
			except Newsletter.DoesNotExist:
				newsletter = Newsletter.objects.create()

			# Begin csv analysis
			csv_success = self.make_playlists_from_csv(newsletter, csv_url)

			if csv_success:
				return HttpResponseRedirect('/preview/')				
			else:
				response = HttpResponse("Didn't work due to errors.", content_type="text/plain")
				return response
		else:
			# get them to resubmit the form
			return HttpResponseRedirect('/invalid/')

	def make_playlists_from_csv(self, newsletter, url):
		"""
		dir = str
		filename = str, with extension
		/Users/andkon/Developer/StringsBackend
		moodcsv.csv
		"""
		import csv
		# import os
		import urllib2
		import StringIO


		# INPUT_DIR = dir
		# file = os.path.join(INPUT_DIR,filename)
		# reader = csv.DictReader(open(file, "rU"), dialect="excel")

		response = urllib2.urlopen(url)
		reader = csv.DictReader(response, dialect="excel")

		# first, make sure you've made a newsletter
		# an emoji set
		# and all the emoji in that set.
		successful_playlists = 0
		for playlist_dict in reader:

			new_playlist = Playlist.objects.create(
				url = playlist_dict['url'],
				title = playlist_dict['title']
			)
			print "Made the playlist"
			sys.stdout.flush()
			new_playlist.description = playlist_dict['description']
			new_playlist.genre = playlist_dict['genre']
			if playlist_dict['ranking'] == '':
				pass
			else:
				new_playlist.ranking = playlist_dict['ranking']
			new_playlist.service = playlist_dict['service']
			new_playlist.save()

			emoji = newsletter.emoji_set.emojis.get(emoji_for_sets__position = playlist_dict['position'])

			new_through_playlist = NewsletterPlaylist(
				playlist = new_playlist,
				newsletter = newsletter,
				position = playlist_dict['position']
			)
			new_through_playlist.save()
			successful_playlists += 1

		resp_str = "It worked! %s playlists added to newsletter %s" % (successful_playlists, newsletter.pk)
		response = HttpResponse(resp_str, content_type="text/plain")
		return response

	@method_decorator(login_required)
	def dispatch(self, *args, **kwargs):
		return super(NewNewsletter, self).dispatch(*args, **kwargs)
			