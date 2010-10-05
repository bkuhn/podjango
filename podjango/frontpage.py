# Copyright 2010       Bradley M. Kuhn <bkuhn@ebb.org>
# Copyright 2005-2008  James Garrison

# This software's license gives you freedom; you can copy, convey,
# propagate, redistribute, modify and/or redistribute modified versions of
# this program under the terms of the GNU Affero General Public License
# (AGPL) as published by the Free Software Foundation (FSF), either
# version 3 of the License, or (at your option) any later version of the
# AGPL published by the FSF.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero
# General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program in a file in the toplevel directory called
# "AGPLv3".  If not, see <http://www.gnu.org/licenses/>.

from django.shortcuts import render_to_response
from podjango.apps.cast.models import Cast
from datetime import datetime, timedelta

def view(request):
    """Cast front page view
    Performs all object queries necessary to render the front page.
    """

    cast = Cast.objects.all().filter(pub_date__lte=datetime.now())[:3]

    c = {
        'cast': cast,
    }
    return render_to_response("frontpage.html", c)
