"""
sentry.search.elasticsearch.backend
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2010-2013 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from __future__ import absolute_import

from collections import defaultdict
from pyelasticsearch import ElasticSearch

from sentry.search.base import SearchBackend

# TODO: ensure upgrade creates search schemas
# TODO: optimize group indexing so it only happens when a group is updated
# TODO: only index an event after a group is indexed??
# TODO: confirm replication=async is a good idea
# TODO: determine TTL
# TODO: index.routing.allocation.include.tag = project_id?


class ElasticSearchBackend(SearchBackend):
    def __init__(self, **options):
        self.backend = ElasticSearch(**options)

    def index(self, event):
        from sentry.app import app

        group = event.group

        app.search.index(
            index='sentry',
            doc_type='group',
            doc=self.document_for_group(group),
            id=group.id,
            replication='async',
        )
        app.search.index(
            index='sentry',
            doc_type='event',
            doc=self.document_for_event(event),
            id=event.id,
            parent=group.id,
            replication='async',
        )

    def schema_for_event():
        return {
            'group': {
                '_parent': {
                    'type': 'group',
                }
            }
        }

    def schema_for_group():
        return {
        }

    def document_for_group(self, group):
        doc = {
            'datetime': group.last_seen,
            'project': group.project.id,
            'team': group.team.id,
        }

        return doc

    def document_for_event(event):
        doc = defaultdict(list)
        for interface in event.interfaces.itervalues():
            for k, v in interface.get_search_context(event).iteritems():
                doc[k].extend(v)
        doc = dict(doc)

        doc['text'].extend([
            event.message,
            event.logger,
            event.server_name,
            event.culprit,
        ])

        doc.update({
            'datetime': event.datetime,
            'project': event.project.id,
            'team': event.team.id,
        })

        return doc
