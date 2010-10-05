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
from django.contrib import admin
from models import CastTag, Cast

class CastTagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('label',)}

admin.site.register(CastTag, CastTagAdmin)

class CastAdmin(admin.ModelAdmin):
    list_display = ('pub_date', 'title')
    list_filter = ['pub_date']
    date_hierarchy = 'pub_date'
    search_fields = ['title', 'summary', 'body']
    prepopulated_fields = {'slug': ("title",)}
    filter_horizontal = ('tags',)


admin.site.register(Cast, CastAdmin)
