"""
sentry.search.solr.backend
~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2010-2013 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from __future__ import absolute_import

from collections import defaultdict
from pysolr import Solr

from sentry.search.base import SearchBackend

# TODO: ensure upgrade creates search schemas
# TODO: optimize group indexing so it only happens when a group is updated
# TODO: only index an event after a group is indexed??
# TODO: confirm replication=async is a good idea
# TODO: determine TTL
# TODO: index.routing.allocation.include.tag = project_id?


class SolrBackend(SearchBackend):
    def __init__(self, url, **options):
        self.backend = Solr(url, **options)

    def index(self, event):
        self.backend.add([
            self._make_document(event),
        ])

    def _make_document(self, event):
        group = event.group

        context = {
            'text': [
                event.message,
                event.culprit
            ],
            'filters': defaultdict(list),
        }
        for interface in event.interfaces.itervalues():
            for k, v in interface.get_search_context(event).iteritems():
                if k == 'text':
                    context[k].extend(v)
                elif k == 'filters':
                    for f_k, f_v in v.iteritems():
                        context[k][f_k].extend(f_v)

        tags = []
        for k, v in context['filters'].iteritems():
            tags.extend('%s=%s' % (k, f_v) for f_v in v)

        doc = {
            'id': group.id,
            'datetime': group.last_seen,
            'project': group.project.id,
            'team': group.team.id,
            'text': filter(bool, context['text']),
            'tags': tags,
        }

        return doc
