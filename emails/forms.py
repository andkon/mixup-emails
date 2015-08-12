from django import forms
from django.forms.extras.widgets import SelectDateWidget
import datetime


class PlaylistCsvForm(forms.Form):
	newsletter_edition = forms.IntegerField(label="Newsletter Edition")
	url = forms.URLField(label="CSV URL")



class NewsletterDateForm(forms.Form):
	datetime_to_send = forms.DateTimeField(label="Send on", widget=SelectDateWidget)


class NewsletterNextMondayForm(forms.Form):
	datetime_to_send = forms.DateTimeField(label="Send next Monday", initial=datetime.date.today)

class EmailSubscribeForm(forms.Form):
	email = forms.EmailField(label="", widget=forms.EmailInput(attrs={'placeholder': 'E-mail address'}))

# class DateSelectorWidget(widgets.MultiWidget):
# 	def __init__(self, attrs=None):
# 		# create choices for days, months, years
# 		# example below, the rest snipped for brevity.
# 		years = [(year, year) for year in (2014, 2015, 2016, 2017, 2018, 2019, 2020,)]
# 		months = [(month, mt) for ]
# 		_widgets = (
# 			widgets.Select(attrs=attrs, choices=days),
# 			widgets.Select(attrs=attrs, choices=months),
# 			widgets.Select(attrs=attrs, choices=years),
# 			widgets.Select(attrs=attrs, choices=hours),
# 			widgets.Select(attrs=attrs, choices=minutes),
# 			widgets.Select(attrs=attrs, choices=seconds),
# 		)
# 		super(DateSelectorWidget, self).__init__(_widgets, attrs)

# 	def decompress(self, value):
# 		if value:
# 			return [value.day, value.month, value.year, value.hours, value.minutes, value.seconds]
# 		return [None, None, None, None, None, None]

# 	def format_output(self, rendered_widgets):
# 		return u''.join(rendered_widgets)

# 	def value_from_datadict(self, data, files, name):
# 		datelist = [
# 			widget.value_from_datadict(data, files, name + '_%s' % i)
# 			for i, widget in enumerate(self.widgets)]
# 		try:
# 			D = date(day=int(datelist[0]), month=int(datelist[1]),
# 					year=int(datelist[2]), hour=int(datelist[3]), minute=int(datelist[4]), second=int(datelist[5]),)
# 		except ValueError:
# 			return ''
# 		else:
# 			return str(D)