from datetime import date
from django.conf import settings
from django.utils.http import int_to_base36, base36_to_int
from django.utils.crypto import constant_time_compare, salted_hmac
from django.utils import six

class EmailProfileTokenGenerator(object):
	"""
	Strategy object used to generate and check tokens for the password
	reset mechanism.
	"""
	def make_token(self, email_profile):
		"""
		Returns a token that can be used once to do a password reset
		for the given user.
		"""
		return self._make_token_with_timestamp(email_profile, self._num_days(self._today()))

	def check_token(self, email_profile, token):
		"""
		Check that a password reset token is correct for a given user.
		"""
		# Parse the token
		try:
			ts_b36, hash = token.split("-")
		except ValueError:
			return False

		try:
			ts = base36_to_int(ts_b36)
		except ValueError:
			return False

		# Check that the timestamp/uid has not been tampered with
		if not constant_time_compare(self._make_token_with_timestamp(email_profile, ts), token):
			return False

		# Check the timestamp is within limit
		if (self._num_days(self._today()) - ts) > settings.PASSWORD_RESET_TIMEOUT_DAYS:
			return False

		return True

	def _make_token_with_timestamp(self, email_profile, timestamp):
		# timestamp is number of days since 2001-1-1.  Converted to
		# base 36, this gives us a 3 digit string until about 2121
		ts_b36 = int_to_base36(timestamp)

		# By hashing on the internal state of the user and using state
		# that is sure to change (the password salt will change as soon as
		# the password is set, at least for current Django auth, and
		# last_login will also change), we produce a hash that will be
		# invalid as soon as it is used.
		# We limit the hash to 20 chars to keep URL short
		key_salt = "django.contrib.auth.tokens.PasswordResetTokenGenerator"

		# Ensure results are consistent across DB backends
		join_timestamp = '' if email_profile.joined is None else email_profile.joined.replace(microsecond=0, tzinfo=None)

		value = (six.text_type(email_profile.pk) +
				six.text_type(join_timestamp) + 
				six.text_type(timestamp) + 
				six.text_type(email_profile.is_confirmed) + 
				six.text_type(email_profile.is_subscribed))
		hash = salted_hmac(key_salt, value).hexdigest()[::2]
		return "%s-%s" % (ts_b36, hash)

	def _num_days(self, dt):
		return (dt - date(2001, 1, 1)).days

	def _today(self):
		# Used for mocking in tests
		return date.today()

default_token_generator = EmailProfileTokenGenerator()