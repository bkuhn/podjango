#  Copyright (C) 2008, 2010 Bradley M. Kuhn <bkuhn@ebb.org>
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

from django.contrib.syndication.feeds import Feed
from django.utils.feedgenerator import Rss201rev2Feed 
#from podjango.apps.staff.models import Person
from podjango.apps.cast.models import Cast

from django.shortcuts import render_to_response
from django.conf import settings
from datetime import datetime

import itertools
import operator

# FIXME: Settings here should not be hard-coded for given casts, but
# should instead have settings from the main screen.

class CastFeedBase(Feed):
    def copyright_holder(self): return "Bradley M. Kuhn, Karen M. Sandler"

    def license_no_html(self): return "Licensed under a Creative Commons Attribution-No Derivative Works 3.0 United States License."

    def item_copyright(self, item):
        year = 2008
        for attr in ('pub_date', 'date_created', 'date_last_modified'):
            if hasattr(item, attr):
                if hasattr(getattr(item, attr), 'year'):
                    year = getattr(getattr(item, attr), 'year')
                    break
        return 'Copyright (C) %d, %s.  %s' % (year, self.copyright_holder(), self.license_no_html())

    def item_extra_kwargs(self, item):
        year = 2008
        for attr in ('pub_date', 'date_created', 'date_last_modified'):
            if hasattr(item, attr):
                if hasattr(getattr(item, attr), 'year'):
                    year = getattr(getattr(item, attr), 'year')
                    break
        return { 'year' : year }

def for_podcast_feed_extra_kwargs(self, obj):
    return { 'managingEditorNames' : 'Bradley and Karen',
             'rssImage' : { 'url' : 'http://faif.us/img/cast/faif_200x200.jpg',
                            'width' : '200', 'height' : '200' },
             'webMaster' : 'oggcast@faif.org',
             'dcCreator' : 'oggcast@faif.org (Bradley and Karen)',
             'iTunesExplicit'  : 'No',
             'iTunesBlock' : 'No',
             'iTunesImage' : { 'url' : 'http://faif.us/img/cast/faif_300x300.jpg',
                               'title' : 'Free as in Freedom',
                               'link' : self.author_link,
                               'type' : 'video/jpg'},
             'category' : { 'name' : 'Technology', 'scheme' : 'http://www.itunes.com/dtds/podcast-1.0.dtd',
                            'subcats' : [ 'Computers', 'Information Technology', 'Operating Systems' ] },
             'keywords' : 'open source, opensource, freesoftware, software freedom, legal, law, linux, free, license, gpl, lgpl, agpl, bsd',
             'iTunesAuthor' : 'Free as in Freedom',
             'iTunesSubtitle' : 'Bi-Weekly Discussion of Legal, Policy, and Any other Issues in the Free, Libre, and Open Source Software (FLOSS) Community',
             'copyrightHolder' : self.copyright_holder(),
             'copyrightLicense' : self.license_no_html() }

def for_podcast_item_extra_kwargs(self, item):
    return { 'duration' : item.duration,
             'year' : item.date_created.year,
             'dcCreator' : 'oggcast@faif.us (Bradley and Karen)',
             'intheitembkuhn' : item.__dict__.__str__()}

def podcast_helper_add_root_elements(self, handler):
    handler.addQuickElement('managingEditor', self.feed['author_email'] 
                            + ' (' + self.feed['managingEditorNames'] + ')')
    handler.startElement('image', {})
    handler.addQuickElement('url', self.feed['rssImage']['url'])
    handler.addQuickElement('title', self.feed['author_name'])
    handler.addQuickElement('link', self.feed['link'])
    handler.addQuickElement('width', self.feed['rssImage']['width'])
    handler.addQuickElement('height', self.feed['rssImage']['height'])
    handler.endElement('image')
    
    handler.addQuickElement('webMaster', self.feed['webMaster'])
    handler.addQuickElement('dc:creator', self.feed['dcCreator'])
    handler.addQuickElement('itunes:explicit', self.feed['iTunesExplicit'])
    handler.addQuickElement('itunes:block', self.feed['iTunesBlock'])
    handler.addQuickElement('generator', 'http://www.faif.us/code')
    
    handler.addQuickElement('media:thumbnail', '' , { 'url' : self.feed['rssImage']['url'] })
    handler.addQuickElement('itunes:image', '' , { 'href' : self.feed['iTunesImage']['url'])
    handler.addQuickElement('itunes:link', '', { 'href' : self.feed['iTunesImage']['url'],
                                                 'type' : self.feed['iTunesImage']['type']})
    
    handler.addQuickElement(u"media:category", self.feed['category']['name'],
                            { 'scheme': self.feed['category']['scheme']})
    if not (self.feed['category']['subcats'] and len(self.feed['category']['subcats']) > 0): 
        handler.addQuickElement(u"itunes:category", '', { 'text': self.feed['category']['name']})
    else:
        handler.startElement(u"itunes:category", { 'text': self.feed['category']['name']})
        for cc in self.feed['category']['subcats']:
            handler.addQuickElement(u"itunes:category", '', { 'text': cc })
        handler.endElement(u"itunes:category")

    handler.addQuickElement(u"media:keywords", self.feed['keywords'].replace(" ", ","))
    
    handler.startElement(u"itunes:owner", {})
    handler.addQuickElement(u"itunes:email", self.feed['author_email'])
    handler.addQuickElement(u"itunes:name", self.feed['author_name'])
    handler.endElement(u"itunes:owner")
    
    handler.addQuickElement(u"itunes:summary", self.feed['description'])
    handler.addQuickElement(u"itunes:subtitle", self.feed['iTunesSubtitle'])
    
    handler.addQuickElement(u"itunes:author", self.feed['iTunesAuthor'])
    handler.addQuickElement(u'atom:link', '', { 'rel' : "self",  'href'  : self.feed['feed_url'],
                                                'type' : "application/rss+xml"})
    
    years = {}
    for ii in self.items: years[ii['year']] = 1
    
    copyrightString = ""
    ll = years.keys()
    ll.sort()
    for yy in ll: copyrightString += "%d, " % yy 
    copyrightString += "%s.  %s" % (self.feed['copyrightHolder'], self.feed['copyrightLicense'])
    
    handler.addQuickElement('copyright', copyrightString)
    handler.addQuickElement('media:copyright', "Copyright (C) " + copyrightString)
    
def podcast_helper_add_item_elements(self, handler, item):
    handler.addQuickElement("itunes:explicit", self.feed['iTunesExplicit'])
    handler.addQuickElement("itunes:block", self.feed['iTunesBlock'])
    handler.addQuickElement(u"itunes:keywords", self.feed['keywords'])
    handler.addQuickElement('dc:creator', self.feed['dcCreator'])
    handler.addQuickElement("itunes:author", item['author_name'])
    handler.addQuickElement("itunes:duration", item['duration'])
    handler.addQuickElement('media:content', '', { 'url' : item['enclosure'].url,
                                                   'fileSize' : item['enclosure'].length,
                                                   'type' : item['enclosure'].mime_type})

class OmnibusFeedType(Rss201rev2Feed):
    def root_attributes(self):
        attrs = super(OmnibusFeedType, self).root_attributes()
        attrs['xmlns:itunes'] = 'http://www.itunes.com/dtds/podcast-1.0.dtd'
        attrs['xmlns:atom'] = 'http://www.w3.org/2005/Atom'
        attrs['xmlns:media'] = 'http://search.yahoo.com/mrss/'
        attrs['xmlns:dc'] = "http://purl.org/dc/elements/1.1/"
        return attrs

    def add_root_elements(self, handler):
        super(OmnibusFeedType, self).add_root_elements(handler)
        podcast_helper_add_root_elements(self, handler)

    def add_item_elements(self, handler, item):
        super(OmnibusFeedType, self).add_item_elements(handler, item)

        # The below is a bit of a cheat, I assume anything in the ominbus
        # feed that has an enclosure must be a podcast.  Probably not true
        # as such in the general case, but enough for this case, I think.
        if item['enclosure']:
            podcast_helper_add_item_elements(self, handler, item)
        else:
            # Block things that don't have an enclosure from iTunes in
            # case someone uploads this feed there.
            handler.addQuickElement("itunes:block", 'Yes')



# http://www.feedforall.com/itune-tutorial-tags.htm
# http://www.feedforall.com/mediarss.htm
class iTunesFeedType(Rss201rev2Feed):
    def root_attributes(self):
        attrs = super(iTunesFeedType, self).root_attributes()
        attrs['xmlns:itunes'] = 'http://www.itunes.com/dtds/podcast-1.0.dtd'
        attrs['xmlns:atom'] = 'http://www.w3.org/2005/Atom'
        attrs['xmlns:media'] = 'http://search.yahoo.com/mrss/'
        attrs['xmlns:dc'] = "http://purl.org/dc/elements/1.1/"
        return attrs

    def add_root_elements(self, handler):
        super(iTunesFeedType, self).add_root_elements(handler)
        podcast_helper_add_root_elements(self, handler)

    def add_item_elements(self, handler, item):
        super(iTunesFeedType, self).add_item_elements(handler, item)
        podcast_helper_add_item_elements(self, handler, item)


class CastFeed(CastFeedBase):
    feed_type = iTunesFeedType
    title = "Free as in Freedom"
    link = "/cast/"
    description = "A bi-weekly discussion of legal, policy, and other issues in the FLOSS world, including interviews from Brooklyn, New York, USA.  Presented by Karen Sandler and Bradley M. Kuhn."
    author_email = "podcast@faif.us"
    author_link = "http://www.faif.us/"
    author_name = "Free as in Freedom"
    title_template = "feeds/podcast_title.html"
    description_template = "feeds/podcast_description.html"
    def items(self):
        return Cast.objects.filter(pub_date__lte=datetime.now()).order_by('-pub_date')
    def item_pubdate(self, item):
        return item.pub_date

    def item_link(self, item):
        return item.get_absolute_url()

    def item_author_email(self, obj):
        return "oggcast@faif.us"

    def item_author_name(self, obj):
        return "Free as in Freedom"

    def item_author_link(self, obj):
        return "http://faif.us"

    def item_categories(self, item):
        return  ('Technology',)

    def copyright_holder(self): return "Free as in Freedom"

    def license_no_html(self): return "Licensed under a Creative Commons Attribution-Share Alike 3.0 Unported License."

    def feed_extra_kwargs(self, obj):
        return for_podcast_feed_extra_kwargs(self, obj)

    def item_extra_kwargs(self, item):
        return for_podcast_item_extra_kwargs(self, item)

# FIXME: 
# GUEST NAME GOES HERE!!!
#<itunes:author>
#     If applicable, at the item level, this tag can contain information
#     about the person(s) featured on a specific episode.


class Mp3CastFeed(CastFeed):
    def item_enclosure_mime_type(self): return "audio/mpeg"
    def item_enclosure_url(self, item):
        return "http://faif.us" + item.mp3_path
    def item_enclosure_length(self, item):
        return item.mp3_length

class OggCastFeed(CastFeed):
    def item_enclosure_mime_type(self): return "audio/ogg"
    def item_enclosure_url(self, item):
        return "http://faif.us" + item.ogg_path
    def item_enclosure_length(self, item):
        return item.ogg_length

feed_dict = {
    'cast-ogg': OggCastFeed,
    'cast-mp3': Mp3CastFeed,
}

# make each feed know its canonical url
for k, v in feed_dict.items():
    v.get_absolute_url = '/feeds/%s/' % k

def view(request):
    """Listing of all available feeds
    """

    feeds = feed_dict.values()
    return render_to_response("feeds.html", {'feeds': feeds})
