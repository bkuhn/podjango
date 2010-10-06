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
from django.conf.urls.defaults import *
from models import Cast, CastTag # relative import
from datetime import datetime

extra_context = {}

info_dict = {
    'queryset': Cast.objects.all(),
    'date_field': 'pub_date',
    'extra_context': extra_context,
}

urlpatterns = patterns('django.views.generic.date_based',
   (r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/(?P<slug>[-\w]+)/$', 'object_detail', dict(info_dict, slug_field='slug')),
   (r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/$', 'archive_day', info_dict),
   (r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/$', 'archive_month', info_dict),
   (r'^(?P<year>\d{4})/$', 'archive_year', dict(info_dict,
                                                make_object_list=True)),
# FIXME HOW DO I MAKE THE SLUG WORK WITH NO DATES IN IT.
#   (r'^(?P<slug>[-\w]+)/$', 'object_detail', dict(info_dict, slug_field='slug')),
)

urlpatterns += patterns('apps.podcast.views',
   (r'^/?$', 'custom_index', dict(info_dict, paginate_by=20)),
   (r'^query/$', 'query'),
)

# Code to display authors and tags on each blog page

def all_tags_by_use_amount():
    """Returns all tags with an added 'cnt' attribute (how many times used)

    Also sorts the tags so most-used tags appear first.
    """

    # tally use amount
    retval = []
    current = None
    for obj in CastTag.objects.filter(podcast__pub_date__lte=datetime.now(),
                                       podcast__isnull=False).order_by('label'):
        if current is not None and obj.id == current.id:
            current.cnt += 1
        else:
            if current is not None:
                retval.append(current)
            current = obj
            current.cnt = 1
    if current is not None:
        retval.append(current)

    # sort and return
    retval.sort(key=lambda x: -x.cnt)
    return retval

# The functions are passed to the context uncalled so they will be
# called for each web request.  If we want to only make these database
# queries a single time when a web server process begins, call both
# functions below (i.e. make both lines below end in '()')

extra_context['all_tags'] = all_tags_by_use_amount
