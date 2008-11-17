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

# FIXME: There are lot of SFLC hard-codes in this file.

from django.contrib.syndication.feeds import Feed
from django.utils.feedgenerator import Rss201rev2Feed 
from sflc.apps.blog.models import Entry as BlogEntry
from sflc.apps.blog.models import EntryTag as BlogEntryTag
from sflc.apps.staff.models import Person
from sflc.apps.news.models import PressRelease
from sflc.apps.podcast.models import Podcast
from sflc.apps.events.models import Event, EventMedia
from sflc.apps.events.view_helpers import organize_media_by_event

from django.shortcuts import render_to_response
from django.conf import settings
from datetime import datetime

import itertools
import operator

class SFLCFeedBase(Feed):
    def copyright_holder(self): return "Software Freedom Law Center"

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
             'rssImage' : { 'url' : 'http://www.softwarefreedom.org/img/podcast/sflc-key-200x200.jpg',
                            'width' : '200', 'height' : '200' },
             'webMaster' : 'press@softwarefreedom.org',
             'dcCreator' : 'podcast@softwarefreedom.org (Bradley and Karen)',
             'iTunesExplicit'  : 'No',
             'iTunesBlock' : 'No',
             'iTunesImage' : { 'url' : 'http://www.softwarefreedom.org/img/podcast/sflc-key-blue-background-with-text_300x300.jpg',
                               'title' : 'Software Freedom Law Center',
                               'link' : self.author_link,
                               'type' : 'video/jpg'},
             'category' : { 'name' : 'Technology', 'scheme' : 'http://www.itunes.com/dtds/podcast-1.0.dtd',
                            'subcats' : [ 'Computers', 'Information Technology', 'Operating Systems' ] },
             'keywords' : 'open source opensource freesoftware software freedom legal law linux free license gpl lgpl agpl bsd',
             'iTunesAuthor' : 'Software Freedom Law Center',
             'iTunesSubtitle' : 'Bi-Weekly Discussion of Legal Issues in the Free, Libre, and Open Source Software (FLOSS) World',
             'copyrightHolder' : self.copyright_holder(),
             'copyrightLicense' : self.license_no_html() }

def for_podcast_item_extra_kwargs(self, item):
    return { 'duration' : item.duration,
             'year' : item.date_created.year,
             'dcCreator' : 'podcast@softwarefreedom.org (Bradley and Karen)',
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
    handler.addQuickElement('generator', 'http://www.softwarefreedom.org/code')
    
    handler.addQuickElement('media:thumbnail', '' , { 'url' : self.feed['rssImage']['url'] })
    handler.startElement('itunes:image', {})
    handler.addQuickElement('url', self.feed['iTunesImage']['url'])
    handler.addQuickElement('title', self.feed['iTunesImage']['title'])
    handler.addQuickElement('link', self.feed['iTunesImage']['link'])
    handler.endElement('itunes:image')
    
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


class OmnibusFeed(SFLCFeedBase):
    feed_type = OmnibusFeedType
    link ="/omnibus/"
    title = "The Software Freedom Law Center"
    description = "An aggregated feed of all RSS content available from the Software Freedom Law Center, including news items, blogs, podcasts, and future events."
    title_template = "feeds/omnibus_title.html"
    description_template = "feeds/omnibus_description.html"
    author_email = "info@softwarefreedom.org"
    author_link = "http://www.softwarefreedom.org/"
    author_name = "Software Freedom Law Center"

    def item_enclosure_mime_type(self): return "audio/mpeg"

    def item_enclosure_url(self, item):
        if hasattr(item, 'mp3_path'):
            return "http://www.softwarefreedom.org" + item.mp3_path
    def item_enclosure_length(self, item):
        if hasattr(item, 'mp3_path'):
            return item.mp3_length

    def item_pubdate(self, item):
        return item.pub_date

    def item_author_name(self, item):
        if item.omnibus_type == "blog":
            return item.author.formal_name
        elif item.omnibus_type == "podcast":
            return "Software Freedom Law Show"
        else:
            return "Software Freedom Law Center"

    def item_author_link(self, obj):
        return "http://www.softwarefreedom.org"

    def item_author_email(self, item):
        if item.omnibus_type == "news":
            return "press@softwarefreedom.org"
        elif item.omnibus_type == "podcast":
            return "podcast@softwarefreedom.org"
        elif hasattr(item, 'author'):
            return "%s@softwarefreedom.org" % item.author
        else:
            return "info@softwarefreedom.org"

    def item_pubdate(self, item):
        if item.omnibus_type == "event":
            return item.date_created
        else:
            return item.pub_date

    def item_link(self, item):
        return item.get_absolute_url()

# http://groups.google.ca/group/django-users/browse_thread/thread/d22e8a8f378cf0e2

    def items(self):
        blogs = BlogEntry.objects.filter(pub_date__lte=datetime.now()).order_by('-pub_date')[:25]
        for bb in blogs:
            bb.omnibus_type = "blog"
            bb.omnibus_feed_description_template = "feeds/blog_description.html"
            bb.omnibus_feed_title_template = "feeds/blog_title.html"

        news = PressRelease.objects.filter(pub_date__lte=datetime.now(),
                                           sites__id__exact=settings.SITE_ID).order_by('-pub_date')[:25]
        for nn in news:
            nn.omnibus_type = "news"
            nn.omnibus_feed_description_template = "feeds/news_description.html"
            nn.omnibus_feed_title_template = "feeds/news_title.html"


        events = Event.future.order_by('-date_created')[:25]
        for ee in events:
            ee.omnibus_type = "event"
            ee.omnibus_feed_description_template = "feeds/future-events_description.html"
            ee.omnibus_feed_title_template = "feeds/future-events_title.html"
            # events don't have a pub_date, so change it to date_created

        podcasts =  Podcast.objects.filter(pub_date__lte=datetime.now()).order_by('-pub_date')
        for pp in podcasts:
            pp.omnibus_type = "podcast"
            pp.omnibus_feed_description_template = "feeds/podcast_description.html"
            pp.omnibus_feed_title_template = "feeds/podcast_title.html"

        a  = [ ii for ii in itertools.chain(blogs, news, events, podcasts)]
        a.sort(key=operator.attrgetter('pub_date'), reverse=True)
        return a

    def feed_extra_kwargs(self, obj):
        # Currently podcast feed is the only one that has a special dict
        # returned here.
        return for_podcast_feed_extra_kwargs(self, obj)

    def item_extra_kwargs(self, item):
        # Currently podcast feed is the only one that has a special dict
        # returned here.
        if item.omnibus_type == 'podcast':
            return for_podcast_item_extra_kwargs(self, item)
        else:
            return super(OmnibusFeed, self).item_extra_kwargs(item)

class BlogFeed(SFLCFeedBase):
    link = "/blog/"

    def title(self):
        answer = "The Software Freedom Law Center Blog"

        GET = self.request.GET
        tags = []
        if 'author' in GET:
            tags = GET.getlist('author')
        if 'tag' in GET:
            tags += GET.getlist('tag')

        if len(tags) == 1:
            answer += " (" + tags[0] + ")"
        elif len(tags) > 1:
            firstTime = True
            done = {}
            for tag in tags:
                if done.has_key(tag): continue
                if firstTime:
                    answer += " ("
                    firstTime = False
                else:
                    answer += ", "
                answer += tag
                done[tag] = tag
            answer += ")"
        else:
            answer += "."
        return answer
        
    def description(self):
        answer = "Blogs at the Software Freedom Law Center"

        GET = self.request.GET
        tags = []
        if 'author' in GET: tags = GET.getlist('author')
        if 'tag' in GET:    tags += GET.getlist('tag')

        done = {}
        if len(tags) == 1:
            answer += " tagged with " + tags[0]
        elif len(tags) > 1:
            firstTime = True
            for tag in tags:
                if done.has_key(tag): continue
                if firstTime:
                    answer += " tagged with "
                    firstTime = False
                else:
                    answer += " or "
                answer += tag
                done[tag] = tag
        else:
            answer = "All blogs at the Software Freedom Law Center"
        answer += "."

        return answer
        
    def item_author_name(self, item):
        return item.author.formal_name

    def item_author_email(self, item):
        GET = self.request.GET
        if not 'author' in GET:
            return "%s@softwarefreedom.org" % item.author
        else:
            answer = ""
            authors = GET.getlist('author')
            firstTime = True
            for author in authors:
                if not firstTime:
                    answer = "%s@softwarefreedom.org" % author
                    firstTime = False
                else:
                    answer += ",%s@softwarefreedom.org" % author

    def item_pubdate(self, item):
        return item.pub_date
    def items(self):
        GET = self.request.GET

        def OR_filter(field_name, subfield_name, objs):
            from django.db.models import Q
            return reduce(lambda x, y: x | y,
                          [Q(**{'%s__%s' % (field_name, subfield_name): x})
                           for x in objs])

        queryset = BlogEntry.objects.filter(pub_date__lte=datetime.now())

        if 'author' in GET:
            authors = GET.getlist('author')
            queryset = queryset.filter(OR_filter('author', 'username', authors))

        if 'tag' in GET:
            tags = GET.getlist('tag')
            queryset = queryset.filter(OR_filter('tags', 'slug', tags))

        return queryset.order_by('-pub_date')[:10]

class TechBlogFeed(BlogFeed):
    title = "Bradley M. Kuhn's SFLC Blog"
    link = "/blog/?author=bkuhn"
    description = "The Software Freedom Law Center Blog,  written by our Policy Analyst and Technology Director, Bradley M. Kuhn."

    def items(self):
        return BlogEntry.objects.filter(author__username__exact="bkuhn", pub_date__lte=datetime.now()).order_by('-pub_date')[:10]

class PressReleaseFeed(SFLCFeedBase):
    title = "SFLC News Releases"
    link = "/news/"
    description = "News releases from the Software Freedom Law Center."

    def items(self):
        return PressRelease.objects.filter(pub_date__lte=datetime.now(),
                                           sites__id__exact=settings.SITE_ID).order_by('-pub_date')[:10]

    def item_pubdate(self, item):
        return item.pub_date

class UpcomingEventFeed(SFLCFeedBase):
    title = "SFLC Upcoming Events"
    link = "/events/"
    description = "Upcoming appearances by the staff of the Software Freedom Law Center and other events related to software freedom where the SFLC will participate."

    def items(self):
        return Event.future.order_by('-date_created')[:10]

    def item_pubdate(self, item):
        return item.date_created

class RecentEventMediaFeed(SFLCFeedBase):
    title = "SFLC Recent Event Media"
    link = "/events/"
    description = "Audio, video and transcripts from SFLC engagements"

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


class PodcastFeed(SFLCFeedBase):
    feed_type = iTunesFeedType
    title = "The Software Freedom Law Show"
    link = "/podcast/"
    description = "A bi-weekly discussion of legal issues in the FLOSS world, including interviews, from the Software Freedom Law Center offices in New York.  Presented by Karen Sandler and Bradley M. Kuhn."
    author_email = "podcast@softwarefreedom.org"
    author_link = "http://www.softwarefreedom.org/"
    author_name = "Software Freedom Law Show"
    title_template = "feeds/podcast_title.html"
    description_template = "feeds/podcast_description.html"
    def items(self):
        return Podcast.objects.filter(pub_date__lte=datetime.now()).order_by('-pub_date')
    def item_pubdate(self, item):
        return item.pub_date

    def item_link(self, item):
        return item.get_absolute_url()

    def item_author_email(self, obj):
        return "podcast@softwarefreedom.org"

    def item_author_name(self, obj):
        return "Software Freedom Law Show"

    def item_author_link(self, obj):
        return "http://www.softwarefreedom.org"

    def item_categories(self, item):
        return  ('Technology',)

    def copyright_holder(self): return "Software Freedom Law Center"

    def license_no_html(self): return "Licensed under a Creative Commons Attribution-No Derivative Works 3.0 United States License."

    def feed_extra_kwargs(self, obj):
        return for_podcast_feed_extra_kwargs(self, obj)

    def item_extra_kwargs(self, item):
        return for_podcast_item_extra_kwargs(self, item)

# FIXME: 
# GUEST NAME GOES HERE!!!
#<itunes:author>
#     If applicable, at the item level, this tag can contain information
#     about the person(s) featured on a specific episode.


class Mp3PodcastFeed(PodcastFeed):
    def item_enclosure_mime_type(self): return "audio/mpeg"
    def item_enclosure_url(self, item):
        return "http://www.softwarefreedom.org" + item.mp3_path
    def item_enclosure_length(self, item):
        return item.mp3_length

class OggPodcastFeed(PodcastFeed):
    def item_enclosure_mime_type(self): return "audio/ogg"
    def item_enclosure_url(self, item):
        return "http://www.softwarefreedom.org" + item.ogg_path
    def item_enclosure_length(self, item):
        return item.ogg_length

feed_dict = {
    'blog': BlogFeed,
    'podcast-ogg': OggPodcastFeed,
    'podcast-mp3': Mp3PodcastFeed,
    'techblog': TechBlogFeed,
    'news': PressReleaseFeed,
    'future-events': UpcomingEventFeed,
    'omnibus': OmnibusFeed,
#    'event-media': RecentEventMediaFeed,
}

# make each feed know its canonical url
for k, v in feed_dict.items():
    v.get_absolute_url = '/feeds/%s/' % k

def view(request):
    """Listing of all available feeds
    """

    feeds = feed_dict.values()
    feeds.remove(TechBlogFeed)
    return render_to_response("feeds.html", {'feeds': feeds})
