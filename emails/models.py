from django.db import models
from django.contrib.auth.models import User

# Create your models here.

# def upload_pic_to(instance, filename):
# 	import os
# 	from django.utils.timezone import now

# 	instance_name = instance.__class__.__name__
# 	if instance_name is Emoji.__name__:
# 		directory = "emoji"

# 	filename_base, filename_ext = os.path.splitext(filename)
# 	return '%s/%s%s' % (
# 		directory,
# 		now().strftime("%Y%m%d%H%M%S"),
# 		filename_ext.lower(),
# 	)


class EmailProfile(models.Model):
	joined = models.DateTimeField(auto_now_add=True)
	email = models.EmailField(primary_key=True)
	user = models.ForeignKey(User, null=True, blank=True)
	is_subscribed = models.BooleanField(default=True)
	is_confirmed = models.BooleanField(default=False)

	def __unicode__(self):
		return "%s" % (self.email)


class Newsletter(models.Model):
	send_date = models.DateTimeField(null=True, blank=True)
	sent_to = models.ManyToManyField(EmailProfile, related_name='received_newsletters', blank=True, null=True)
	message = models.CharField(max_length=1000, null=True, blank=True)
	subject = models.CharField(max_length=140, null=True, blank=True)
	send_task = models.CharField(max_length=200, null=True, blank=True)

	def __unicode__(self):
		return "Edition %s" % (self.pk)