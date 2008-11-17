#  Copyright (C) 2008       Bradley M. Kuhn <bkuhn@ebb.org>
#  Copyright (C) 2006, 2007 Software Freedom Law Center, Inc.
#
# This software's license gives you freedom; you can copy, convey,
# propogate, redistribute and/or modify this program under the terms of
# the GNU Affero General Public License (AGPL) as published by the Free
# Software Foundation (FSF), either version 3 of the License, or (at your
# option) any later version of the AGPL published by the FSF.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero
# General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program in a file in the toplevel directory called
# "AGPLv3".  If not, see <http://www.gnu.org/licenses/>.
#
from django.db import models
from django.conf import settings
from apps.staff.models import Person
from datetime import datetime, timedelta

class PodcastTag(models.Model):
    """Tagging for podcasts"""

    label = models.CharField(max_length=100)
    slug = models.SlugField()

    class Meta:
        db_table = 'podcast_tags' # legacy

    def __unicode__(self):
        return self.label

    def get_absolute_url(self):
        return u"/podcast/?tag=%s" % self.slug

class Podcast(models.Model):
    """Podcast"""

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    summary = models.TextField(help_text="Use raw HTML.  This summary is not included at the beginning of the body when the entry is displayed.  It used only for the material on the front page.")
    body = models.TextField(help_text="Use raw HTML.  Include the full body of any show notes or other information about this episode.  It will be labelled on the site as Show Notes.  It is included on the detail entry, and in the description data on the podcast RSS feed.")
    pub_date = models.DateTimeField()
    poster = models.ForeignKey(Person)
    tags = models.ManyToManyField(PodcastTag, null=True, blank=True)
    ogg_path = models.CharField(max_length=300, blank=True,
                             help_text="Local filename of the Ogg file, relative to webroot.  File should be uploaded into the static media area for podcasts.")
    mp3_path = models.CharField(max_length=300, blank=True,
                             help_text="Local filename of the mp3 file, relative to webroot.  File should be uploaded into the static media area for podcasts.")
    ogg_length = models.IntegerField(blank=False, help_text="size in bytes of ogg file")
    mp3_length = models.IntegerField(blank=False, help_text="size in bytes of mp3 file")
    duration = models.CharField(max_length=8, blank=False, help_text="length in hh:mm:ss of mp3 file")
    date_created = models.DateTimeField(auto_now_add=True)
    date_last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'podcasts_entries' # legacy
        verbose_name_plural = 'podcasts'
        ordering = ('-pub_date',)
        get_latest_by = 'pub_date'

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return u"/podcast/%s/%s/" % (self.pub_date.strftime("%Y/%b/%d").lower(),
                                  self.slug)
# FIXME
#        return (u"/podcast/%s/" % (self.slug))

    def is_recent(self):
        return self.pub_date > (datetime.now() - timedelta(days=14))
        # question: does datetime.now() do a syscall each time is it called?
