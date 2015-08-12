from __future__ import absolute_import
from celery import shared_task

from django.core import mail
from django.template.loader import render_to_string

import datetime
from .models import *
from .tokens import default_token_generator as token_generator
from django.test.client import RequestFactory
import sys

@shared_task
def send_newsletter(newsletter_id):
	"""
	Let's send everyone their newsletter!
	1) First, get current subscribers.
	2) Then, create messages for them.
	3) Send the emails one-by-one, using Sendgrid.
	"""
	connection = mail.get_connection()
	print "Got connection: %s" % (connection)
	sys.stdout.flush()

	newsletter = Newsletter.objects.get(pk=newsletter_id)
	playlists = newsletter.playlists_through.all().order_by('-position')
	subscribers = EmailProfile.objects.filter(is_subscribed=True, is_confirmed=True)
	for email_profile in subscribers:
		# get body: https://docs.djangoproject.com/en/1.7/ref/templates/api/#module-django.template.loader
		try:
			newsletter.sent_to.get(email=email_profile.email)
		except EmailProfile.DoesNotExist:
			# Cool, now we can send it
			token = token_generator.make_token(email_profile)
			domain_name = 'http://www.xn--7bi.ws'

			html_body = render_to_string('emails/hero_preprocessed.html',
				{'newsletter': newsletter, 
				'email_profile': email_profile, 
				'playlists':playlists,
				'domain_name':domain_name,
				'token': token,
				})

			email = mail.EmailMessage(newsletter.subject, html_body, 'andrew@strings.fm', [email_profile.email], connection=connection)
			email.content_subtype = 'html'
			try:
				email.send(fail_silently=False)
				print "sent email to %s" % (email_profile.email)
				sys.stdout.flush()
				newsletter.sent_to.add(email_profile)
			except Exception as e:
				print "Didn't send to email_profile.email"
				sys.stdout.flush()
				print e
				sys.stdout.flush()
	newsletter.send_date = datetime.datetime.now()
	newsletter.save()

@shared_task
def send_to_andrew(newsletter_id):
	"""
	Let's send everyone their newsletter!
	1) First, get current subscribers.
	2) Then, create messages for them.
	3) Send the emails one-by-one, using Sendgrid.
	"""
	connection = mail.get_connection()
	print "Got connection: %s" % (connection)
	sys.stdout.flush()

	newsletter = Newsletter.objects.get(pk=newsletter_id)
	playlists = newsletter.playlists_through.all().order_by('-position')
	email_profile = EmailProfile.objects.filter(email='andrew@strings.fm').get()
	token = token_generator.make_token(email_profile)
	domain_name = 'http://www.xn--7bi.ws'

	html_body = render_to_string('emails/hero_preprocessed.html',
		{'newsletter': newsletter, 
		'email_profile': email_profile, 
		'playlists':playlists,
		'domain_name':domain_name,
		'token': token,
		})

	email = mail.EmailMessage(newsletter.subject, html_body, 'andrew@strings.fm', [email_profile.email], connection=connection)
	email.content_subtype = 'html'
	try:
		email.send(fail_silently=False)
		print "sent email to andrew"
		sys.stdout.flush()
		newsletter.sent_to.add(email_profile)
	except Exception as e:
		print "Didn't send to email_profile.email"
		sys.stdout.flush()
		print e
		sys.stdout.flush()

@shared_task
def send_confirmation_emails(emails):
	connection = mail.get_connection()
	print "got connection"
	sys.stdout.flush()
	for email in emails:
		try:
			email_profile = EmailProfile.objects.get(email=email)	
		except EmailProfile.DoesNotExist:
			print "email %s doesn't have a profile" % (email)
			email_profile = EmailProfile.objects.create(email=email)

		# Generate an email hash
		token = token_generator.make_token(email_profile)
		print "got email token: %s" % (token)
		sys.stdout.flush()
		# Now it's time to send an email to this homie!
		domain_name = 'http://www.xn--7bi.ws'

		html_body = render_to_string('emails/confirmsubscribe.html', 
			{'email_profile': email_profile, 
			'token': token,
			'domain_name':domain_name,
			})
		print "got email body"
		sys.stdout.flush()
		if email_profile.invited_by:
			subject = "You've been invited to our playlist club!"
		else:
			subject = "Confirm your subscription to 2.ws"
		email = mail.EmailMessage(subject, html_body, 'andrew@strings.fm', [email_profile.email], connection=connection)
		email.content_subtype = 'html'
		print "about to send"
		sys.stdout.flush()
		try:
			email.send(fail_silently=False)
			print "sent email %s" % (email)
			sys.stdout.flush()
		except Exception as e:
			print "Didn't send to %s" % (email)
			sys.stdout.flush()
			print e
			sys.stdout.flush()
	print "Finished all emails"
	sys.stdout.flush()

@shared_task
def send_latest_newsletter_to_emails(emails):
	connection = mail.get_connection()

	latest_newsletter = Newsletter.objects.order_by('-send_date')[0]
	playlists = latest_newsletter.playlists_through.all().order_by('-position')

	for email in emails:
		# get body: https://docs.djangoproject.com/en/1.7/ref/templates/api/#module-django.template.loader
		try:
			email_profile = EmailProfile.objects.get(email=email)	
		except EmailProfile.DoesNotExist:
			print "email %s doesn't have a profile" % (email)
			email_profile = EmailProfile.objects.create(email=email)
		
		token = token_generator.make_token(email_profile)
		domain_name = 'http://www.xn--7bi.ws'

		html_body = render_to_string('emails/hero_preprocessed.html',
			{'newsletter': latest_newsletter, 
			'email_profile': email_profile, 
			'playlists':playlists,
			'domain_name':domain_name,
			'token': token,
			})

		email = mail.EmailMessage(latest_newsletter.subject, html_body, 'andrew@strings.fm', [email_profile.email], connection=connection)
		email.content_subtype = 'html'
		try:
			email.send(fail_silently=False)
			print "sent email %s" % (email.to)
			sys.stdout.flush()
			latest_newsletter.sent_to.add(email_profile)
		except Exception as e:
			print "Didn't send to email_profile.email"
			sys.stdout.flush()
			print e
			sys.stdout.flush()

