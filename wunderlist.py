#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import json
import logging


class WunderlistAPI(object):
    urlapi = 'https://a.wunderlist.com/api/v1'

    def __init__(self, accesstoken, clientid):
        self.accesstoken = accesstoken
        self.clientid = clientid

    def _sendurlrequest(self, endpoint, formdict=None, method=None):
        request = urllib2.Request(self.urlapi + '/' + endpoint)
        request.add_header('X-Access-Token', self.accesstoken)
        request.add_header('X-Client-ID', self.clientid)
        request.add_header('Content-Type', 'application/json')
        if formdict is not None:
            if isinstance(formdict, dict):
                formdict = json.dumps(formdict)
            request.add_data(formdict)
        if method is not None:
            request.get_method = lambda: method
        try:
            logging.info('Endpoint: %s', endpoint)
            logging.info('X-Access-Token: %s', self.accesstoken)
            logging.info('X-Client-ID %s', self.clientid)
            logging.info('Formdict: %s', formdict)
            logging.info('Method: %s', method)
            return urllib2.urlopen(request).read()
        except IOError, e:
            print 'Error:', e

    def memberships(self):
        """
        curl -A "" -s \
        -H "Content-Type: application/json" \
        -H "X-Access-Token: 94c0f1728a3cb4a066d21f1a63da3d4101fa7d11deb78ef800e4b16776e6" \
        -H "X-Client-ID: 171f61134bea341afeff" \
        https://a.wunderlist.com/api/v1/memberships | python -m json.tool
        """
        return self._sendurlrequest('memberships')

    def markmemberaccepted(self, req_id, revision):
        """
        #Dziala poprawnie. Revizja brana jest z membership.sh W dokumentacji jest blad w
        #url daja memberships:id zamist memberships/id
        # id jest brane z membership.sh

        curl -A "" -v -X PATCH \
        -H "Content-Type: application/json" \
        -H "X-Access-Token: 94c0f1728a3cb4a066d21f1a63da3d4101fa7d11deb78ef800e4b16776e6" \
        -H "X-Client-ID: 171f61134bea341afeff" \
        -d '{"revision":1, "state":"accepted"}' \
        https://a.wunderlist.com/api/v1/memberships/152774308
        """

        datareq = {
            'revision': int(revision),
            'state': 'accepted',
            'muted': False,
        }
        return self._sendurlrequest('memberships/'+str(req_id), datareq, 'PATCH')

    def createlist(self, title):
        """
        curl -A "" -s \
        -H "Content-Type: application/json" \
        -H "X-Access-Token: 94c0f1728a3cb4a066d21f1a63da3d4101fa7d11deb78ef800e4b16776e6" \
        -H "X-Client-ID: 171f61134bea341afeff" \
        -d '{"title":"List001"}' \
        https://a.wunderlist.com/api/v1/lists
        """
        datareq = {
            'title': title
        }
        return self._sendurlrequest('lists', datareq, 'POST')

    def createtask(self, list_id, title):
        """
        curl -A "" -s \
        -H "Content-Type: application/json" \
        -H "X-Access-Token: 94c0f1728a3cb4a066d21f1a63da3d4101fa7d11deb78ef800e4b16776e6" \
        -H "X-Client-ID: 171f61134bea341afeff" \
        -d '{"list_id":247639416, "title":"Task1"}' \
        https://a.wunderlist.com/api/v1/tasks | python -m json.tool
        """
        datareq = {
            'list_id': int(list_id),
            'title': title
        }
        return self._sendurlrequest('tasks', datareq, 'POST')

    def removemember(self, req_id, revision):
        """
        memberships/req_id - id wziete z memberships
        revision doklejone do get wziete z memberships

        curl -A "" -v -X DELETE \
        -H "Content-Type: application/json" \
        -H "X-Access-Token: 94c0f1728a3cb4a066d21f1a63da3d4101fa7d11deb78ef800e4b16776e6" \
        -H "X-Client-ID: 171f61134bea341afeff" \
        -d '{"revision":2}' \
        "https://a.wunderlist.com/api/v1/memberships/152617001?revision=2"
        """
        datareq = {
            'revision': int(revision)
        }
        return self._sendurlrequest('memberships/'+str(req_id)+'?revision='+str(revision), datareq, 'DELETE')


if __name__ == '__main__':
    wa = WunderlistAPI('94c0f1728a3cb4a066d21f1a63da3d4101fa7d11deb78ef800e4b16776e6', '171f61134bea341afeff')
    result = wa.memberships()
    result = json.loads(result)
    print result
    for el in result:
        if el['state'] == 'pending':
            print el['id'], el['revision'], el['sender_id'], el['list_id']
#wa.markmemberaccepted(el['id'], el['revision'])
