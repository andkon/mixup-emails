from django.conf.urls import patterns, url
from .views import *

urlpatterns = patterns('',
	# url(r'^$', index, name="index"),
	# View a given newsletter in the browser:
	url(r'^(?P<newsletter_id>[A-Z0-9]+)/$', NewsletterView.as_view(), name="newsletter"),
	url(r'^latest/$', LatestNewsletter.as_view(), name="latest"),
	# View a given newsletter as a given user:
	url(r'^(?P<newsletter_id>[A-Z0-9]+)/(?P<email>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/$', NewsletterEmailView.as_view(), name="user newsletter"),
	# Get redirected to a given playlist	
	url(r'^(?P<newsletter_id>[A-Z0-9]+)/(?P<email>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/(?P<playlist_pk>[A-Z0-9]+)/$', PlaylistEmailRedirect.as_view(), name="playlist redirect for user"),
	url(r'^(?P<newsletter_id>[A-Z0-9]+)/(?P<playlist_pk>[0-9]+)/$', PlaylistRedirect.as_view(), name="playlist redirect"),
	# Sending views
	url(r'^new/$', NewNewsletter.as_view(), name="new-newsletter"),
	url(r'^send/(?P<newsletter_id>[A-Z0-9]+)/$', SendNewsletter.as_view(), name="send-newsletter"),
	url(r'^send/(?P<newsletter_id>[A-Z0-9]+)/confirmcel/$', ConfirmSendCelery.as_view(), name="confirm-send-celery"),
	url(r'^send/(?P<newsletter_id>[A-Z0-9]+)/test/$', TestSend.as_view(), name="confirm-send-test"),
	# Subscription views
	url(r'^subscribe/$', Subscribe.as_view(), name="subscribe"),
	url(r'^confirm/(?P<email>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/(?P<confirmation_hash>[\w\W]+)/$', ConfirmSubscription.as_view(), name="confirm-subscribe"),
	url(r'^resend_confirmation/(?P<email>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/$', ResendConfirmation.as_view(), name="resend-confirmation"),
	url(r'^unsubscribe/(?P<email>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/(?P<confirmation_hash>[\w\W]+)/$', Unsubscribe.as_view(), name="unsubscribe"),
	# Invite views
	url(r'^invite/(?P<email>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/$', InviteFriends.as_view(), name="invite"),
	url(r'^test/(?P<subtest>[\w\W]+)/$', TestTemplate.as_view(), name="test"),
)