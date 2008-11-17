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

class Person(models.Model):
    """Staff members

    Referenced from podcast module
    """

    username = models.CharField(max_length=20)
    formal_name = models.CharField(max_length=200)
    casual_name = models.CharField(max_length=200)
#    title = models.CharField(max_length=200, blank=True)
#    biography = models.TextField(blank=True)
#    phone = models.CharField(max_length=30, blank=True)
#    gpg_key = models.TextField(blank=True)
#    gpg_fingerprint = models.CharField(max_length=100, blank=True)
    currently_employed = models.BooleanField(default=True)

    date_created = models.DateTimeField(auto_now_add=True)
    date_last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'people'

    def __unicode__(self):
        return self.username

    def biography_url(self):
        return u"/about/team/#%s" % self.username

