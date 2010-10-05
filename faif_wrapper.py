# req.subprocess_env is not set when the PostReadRequestHandler runs,
# so we just bypass it altogether and set the relevant variable here.
# See deployment documentation for more info.
from os import environ
environ["DJANGO_SETTINGS_MODULE"] = 'podjango.settings'
environ["CANONICAL_HOSTNAME"] = 'faif.us'

from modpythoncustom import *
