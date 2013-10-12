"""
sentry.search.solr.client
~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2010-2013 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import pysolr

from nydus.db.backends import BaseConnection


class Solr(BaseConnection):
    retryable_exceptions = frozenset()

    def __init__(self, num, url):
        self.url = url
        super(Solr, self).__init__(num)

    @property
    def identifier(self):
        return 'solr+%(url)s' % vars(self)

    def connect(self):
        return pysolr.Solr(self.url)

    def disconnect(self):
        pass
