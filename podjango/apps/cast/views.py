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
from models import Cast, CastTag # relative import
from django.views.generic.list_detail import object_list
from apps.staff.models import Person
from django.shortcuts import get_object_or_404, render_to_response
from datetime import datetime

def OR_filter(field_name, objs):
    from django.db.models import Q
    return reduce(lambda x, y: x | y,
                  [Q(**{field_name: x.id}) for x in objs])

def last_name(person):
    return person.formal_name.rpartition(' ')[2]

def custom_index(request, queryset, *args, **kwargs):
    """Cast list view that allows scrolling and also shows an index by
    year.
    """

    kwargs = kwargs.copy()
    kwargs['extra_context'] = kwargs.get('extra_context', {}).copy()
    extra_context = kwargs['extra_context']

    date_field = kwargs['date_field']
    del kwargs['date_field']

    if not kwargs.get('allow_future', False):
        queryset = queryset.filter(**{'%s__lte' % date_field: datetime.now()})

    authors = []
    if 'author' in request.GET:
        authors = [get_object_or_404(Person, username=author)
                   for author in request.GET.getlist('author')]
        extra_context['authors'] = authors
        queryset = queryset.filter(OR_filter('author', authors))

    tags = []
    if 'tag' in request.GET:
        tags = [get_object_or_404(CastTag, slug=tag)
                for tag in request.GET.getlist('tag')]
        extra_context['tags'] = tags
        queryset = queryset.filter(OR_filter('tags', tags))

    if authors or tags:
        query_string = '&'.join(['author=%s' % a.username for a in authors]
                                + ['tag=%s' % t.slug for t in tags])
        extra_context['query_string'] = query_string

    else:
        date_list = queryset.dates(date_field, 'year')
        extra_context['date_list'] = date_list

    return object_list(request, queryset, *args, **kwargs)

def query(request):
    """Page to query the podcast based on and tags
    """

    if request.GET:
        d = request.GET.copy()
        if 'authors' in d.getlist('all'):
            d.setlist('author', []) # remove author queries
        if 'tags' in d.getlist('all'):
            d.setlist('tag', []) # remove tag queries
        d.setlist('all', []) # remove "all" from the query string

        base_url = '/podcast/'
        if 'rss' in d:
            base_url = '/feeds/podcast/'
            d.setlist('rss', []) # remove it

        query_string = d.urlencode()

        return relative_redirect(request, '%s%s%s' % (base_url, '?' if query_string else '', query_string))

    else:
        tags = CastTag.objects.all().order_by('label')
        return render_to_response('podcast/query.html', {'tags': tags})

def relative_redirect(request, path):
    from django import http
    from django.conf import settings

    host = http.get_host(request)
    if settings.FORCE_CANONICAL_HOSTNAME:
        host = settings.FORCE_CANONICAL_HOSTNAME

    url = "%s://%s%s" % (request.is_secure() and 'https' or 'http', host, path)
    return http.HttpResponseRedirect(url)
