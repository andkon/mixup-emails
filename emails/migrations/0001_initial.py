# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import emails.colourfield
import emails.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailProfile',
            fields=[
                ('email', models.EmailField(max_length=75, serialize=False, primary_key=True)),
                ('signup_source', models.CharField(blank=True, max_length=3, null=True, choices=[(b'FRD', b'Friend signed you up.'), (b'NU', b"'Not you' button in e-mail."), (b'HPG', b'Homepage.')])),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Emoji',
            fields=[
                ('emoji', models.CharField(max_length=2, serialize=False, primary_key=True)),
                ('image', models.ImageField(null=True, upload_to=emails.models.upload_pic_to, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EmojiSet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('emojis', models.ManyToManyField(related_name=b'in_sets', to='emails.Emoji')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Newsletter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('emoji_set', models.ForeignKey(related_name=b'used_in_newsletters', blank=True, to='emails.EmojiSet', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NewsletterPlaylist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('position', models.IntegerField(max_length=2)),
                ('alt_emoji', models.ForeignKey(related_name=b'alt_for_newsletter_playlists', blank=True, to='emails.Emoji', null=True)),
                ('newsletter', models.ForeignKey(related_name=b'playlists_through', to='emails.Newsletter')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Playlist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.URLField()),
                ('title', models.CharField(max_length=200)),
                ('description', models.CharField(max_length=300, null=True, blank=True)),
                ('genre', models.CharField(max_length=50, null=True, blank=True)),
                ('ranking', models.PositiveIntegerField(max_length=1, null=True, blank=True)),
                ('service', models.CharField(max_length=3, choices=[(b'SZA', b'Songza'), (b'SFY', b'Spotify'), (b'RDO', b'Rdio'), (b'8KS', b'8tracks'), (b'NPC', b'Noon Pacific'), (b'BOP', b'Bop.fm'), (b'GSK', b'Grooveshark'), (b'HPM', b'Hype Machine')])),
            ],
            options={
                'verbose_name': 'Playlist',
                'verbose_name_plural': 'Playlists',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PlaylistClick',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('clicked_by', models.ForeignKey(related_name=b'clicked_on', blank=True, to='emails.EmailProfile', null=True)),
                ('clicked_playlist', models.ForeignKey(related_name=b'clicks', to='emails.Playlist')),
                ('newsletter', models.ForeignKey(related_name=b'clicks', blank=True, to='emails.Newsletter', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SettedEmoji',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('position', models.IntegerField(max_length=2)),
                ('color', emails.colourfield.ColourField(max_length=6, null=True, blank=True)),
                ('emoji', models.ForeignKey(related_name=b'emoji_for_sets', to='emails.Emoji')),
                ('emoji_set', models.ForeignKey(related_name=b'emoji_in_set', to='emails.EmojiSet')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='settedemoji',
            unique_together=set([('position', 'emoji')]),
        ),
        migrations.AddField(
            model_name='newsletterplaylist',
            name='playlist',
            field=models.ForeignKey(related_name=b'newsletter_playlist', to='emails.Playlist'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='newsletter',
            name='playlists',
            field=models.ManyToManyField(related_name=b'in_newsletters', null=True, through='emails.NewsletterPlaylist', to='emails.Playlist', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='newsletter',
            name='sent_to',
            field=models.ManyToManyField(related_name=b'received_newsletters', null=True, to='emails.EmailProfile', blank=True),
            preserve_default=True,
        ),
    ]
