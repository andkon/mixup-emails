=====
mixup-emails
=====

mixup-emails is a simple Django app to manage email newsletters.
You can sign new users up, send them confirmation emails,
and send them great content based off of django templates.

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "emails" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        ...
        'emails',
    )

2. Include the emails URLconf in your project urls.py like this::

    url(r'^emails/', include('emails.urls')),

3. Run `python manage.py migrate` to create the emails models.

4. Start the development server and visit http://127.0.0.1:8000/admin/
   to create a poll (you'll need the Admin app enabled).

5. Visit http://127.0.0.1:8000/emails/ to participate in the poll.