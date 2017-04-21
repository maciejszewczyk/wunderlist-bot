#!/usr/bin/env python
# -*- coding: utf-8 -*-

# <app name>.appspot.com
# https://cloud.google.com/appengine/docs/python/ndb/db_to_ndb

import webapp2
import os
import jinja2
import wunderlist
import json
import re
import time

from models import Note
from models import Words
from models import Products2
import string

from google.appengine.ext import ndb
from google.appengine.api import taskqueue
import logging

jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
expirationTime = 600

wa = wunderlist.WunderlistAPI('94c0f1728a3cb4a066d21f1a63da3d4101fa7d11deb78ef800e4b16776e6',
                              '171f61134bea341afeff')


class MainHandler(webapp2.RequestHandler):
    def get(self):
        # do testow manualnych - wylaczych crona i odhaszowac ponizsza linijke
        # self.viewshare()
        #time.sleep(1)
        #bd = self.viewdb()
        template_context = {
            'body': 'koniec'
        }
        template = jinja_env.get_template('templates/main.html')
        self.response.out.write(template.render(template_context))

    @staticmethod
    def viewshare():
        logging.info('!! START function viewshare !!')
        result = wa.memberships()
        result = json.loads(result)
        data = []
        tasks = []
        for el in result:
            if el['state'] == 'pending':  # Czekajace zaproszenie do zaakceptowania listy
                logging.info('!! Jest zaproszenie !!')
                n = Note(id=el['id'],   # nadajemy klucz
                         sender_id=el['sender_id'],
                         list_id=el['list_id'],
                         revision=el['revision'],
                         status=0)
                data.append(n)
                tasks.append(taskqueue.Task(url='/taskmanager',
                                            params={'req_id': el['id'],
                                                    'revision': el['revision'],
                                                    'list_id': el['list_id']}))
        if data:
            ndb.put_multi(data)
            logging.info('!! Dodano listy do bazy !!')
        if tasks:
            q = taskqueue.Queue()
            q.add(tasks)
            logging.info('!! Dodano listy do kolejki !!')
        logging.info('!! STOP function viewshare !!')
        # self.response.write('Task successfully added to the queue.')

    def viewdb(self):
        e = Note.get_by_id(153252103)
        sender_id = getattr(e, 'sender_id')
        list_id = getattr(e, 'list_id')
        revision = getattr(e, 'revision')
        status = 1
        props = {'id': 153252103,
                 'sender_id': sender_id,
                 'list_id': list_id,
                 'revision': revision,
                 'status': status}
        d = Note(**props)
        d.put()
        self.response.write('End viewdb')


class TaskManager(webapp2.RequestHandler):
    def post(self):
        if not 'X-AppEngine-TaskName' in self.request.headers:
            self.error(403)
        req_id = self.request.get('req_id')
        revision = self.request.get('revision')
        list_id = self.request.get('list_id')
        logging.info('!! Task Manager req_id: %s', req_id)
        logging.info('!! Task Manager revision: %s', revision)
        logging.info('!! Task Manager list_id: %s', list_id)
        # Zaakceptuj zaproszenie do listy
        result = wa.markmemberaccepted(req_id, revision)
        logging.info('!! Mark Member Accepted result: %s', result)
        # Stworz taska w zaakceptowanej liscie
        result = wa.createtask(list_id, 'Alistbot wita!')
        logging.info('!! Create Task result: %s', result)
        # Przestan byc memberem listy do ktorej byles zaproszony
        result = wa.memberships()
        result = json.loads(result)
        for el in result:
            if el['id'] == int(req_id):
                wa.removemember(req_id, el['revision'])
                logging.info('!! Remove Member result: OK')


class CronUpdate(webapp2.RequestHandler):
    def post(self):
        self.abort(405, headers=[('Allow', 'GET')])

    def get(self):
        if 'X-AppEngine-Cron' not in self.request.headers:
            self.error(403)
        logging.info("!! Cron Start")
        MainHandler.viewshare()


class Manual(webapp2.RequestHandler):
    def get(self):
        result = wa.memberships()
        result = json.loads(result)
        for el in result:
            if el['id'] == 154184036:
                result = wa.removemember(154184036, el['revision'])
                logging.info('Result: %s', type(el['id']))
                self.response.write('Usuniete')


class Lemmatization(webapp2.RequestHandler):
    def get(self):
        quedict = taskqueue.Queue()
        quedict.add(taskqueue.Task(url='/tasklemmatization', params={'req_id': 1}))
        logging.info('!! Dodano zadanie do kolejki !!')
        self.response.write('Wrzucam dane do LemmatizationDict')


class TaskLemmatization(webapp2.RequestHandler):
    def post(self):
        if not 'X-AppEngine-TaskName' in self.request.headers:
            self.error(403)
        logging.info('!! X-Appengine-TaskName: %s !!' % self.request.headers['X-Appengine-TaskName'])
        logging.info('!! X-AppEngine-TaskRetryCount: %s !!' % self.request.headers['X-AppEngine-TaskRetryCount'])
        logging.info('!! X-AppEngine-TaskExecutionCount: %s !!' % self.request.headers['X-AppEngine-TaskExecutionCount'])
        logging.info('!! X-AppEngine-TaskETA: %s !!' % self.request.headers['X-AppEngine-TaskETA'])
        logging.info('!! X-AppEngine-QueueName: %s !!' % self.request.headers['X-AppEngine-QueueName'])
        filename = os.path.join(os.path.split(__file__)[0], 'dictionary.txt')
        filename = open(filename, 'rU')
        req_id = self.request.get('req_id')
        logging.info('!!! req_id: %s' % req_id)
        datadict = []

        try:
            for line in filename:
                line = line.rstrip()
                # wf - forma slowa np. pomidory
                # nom - mianownik
                wf, nominative = line.split('|')
                ld = Words(word_form=wf,
                           nom=nominative)
                datadict.append(ld)

        finally:
            filename.close()
            if datadict:
                ndb.put_multi(datadict)
                logging.info('!! Utworzylem NDB: Words !!')


class Statistics(webapp2.RequestHandler):
    def get(self):
        self.response.write('Generuje statystyki<br>')
        q = ndb.gql("""SELECT * FROM Words""")
        self.response.write('Dla count NDB Words: %s<br>' % q.count())
        q = ndb.gql("""SELECT * FROM Products2""")
        self.response.write('Dla count NDB Products2: %s<br>' % q.count())


class AddProducts(webapp2.RequestHandler):
    def get(self):
        self.response.write('Wstawiam produkty')
        logging.info('!! Wstawiam produkty')
        filename = os.path.join(os.path.split(__file__)[0], 'productsVegetables_NOPL.txt')
        fo = open(filename, 'rU')
        productsdict = []
        try:
            for line in fo:
                line = line.rstrip()
                L = line.split('|')
                if len(L) == 2:
                    # ma tylko produkt i kategorie: 'ananas|warzywa_owoce'
                    ext = None
                    cat = L[1]
                else:
                    # ma produkt, rozszerzenie i kategorie: 'ananas|puszka|przetwory_owocowe'
                    ext = L[1]
                    cat = L[2]
                pd = Products2(product=L[0],
                              extension=ext,
                              category=cat)
                productsdict.append(pd)
        finally:
            fo.close()
            if productsdict:
                ndb.put_multi(productsdict)
                logging.info('!! Utworzylem NDB o nazwie: Products2 !!')


class Normalization(webapp2.RequestHandler):
    def post(self):
        product = self.request.get('product')
        ret = self._normalize(product)
        logging.info('!! Zwrot z normalizacji: %s' % ret)
        L = ret.split()
        logging.info(L)
        res1, res2, res3 = None, None, None
        if len(L) >= 2:
            # Poszukaj normalizacji dla obu wyrazow
            q1 = Words.query().filter(Words.word_form == L[0])
            q2 = Words.query().filter(Words.word_form == L[1])
            res1 = q1.get()
            res2 = q2.get()
            logging.info('Res1: %s' % res1)
            logging.info('Res2: %s' % res2)
            if res1 is not None and res2 is not None:
                # Wystepuja normalizacje dla obu wyrazow
                q3 = Products2.query(
                    ndb.OR(
                        ndb.AND(
                            Products2.product == res1.nom,
                            Products2.extension == res2.nom
                        ),
                        ndb.AND(
                            Products2.product == res2.nom,
                            Products2.extension == res1.nom
                        )))

                res3 = q3.get()

                logging.info(q3)
                logging.info(res3)
                if res3 is not None:
                    # Znalazl kategorie dla produktu zlozonego z 2 elementow
                    self.response.write('%s %s %s' % (res1.nom, res2.nom, res3.category))
                else:
                    self.response.write('Produkt %s wpada do PLONK_0' % (ret))
            else:
                # Sa 2 wyrazy ale jeden z nich jest None lub oba sa None
                # Szukamy tylko dla L[0] - dajemy ostatnia szanse
                q1 = Words.query().filter(Words.word_form == L[0])
                # uzywamy get() bo spodziewamy sie tylko 1 wyniku
                # pod res1 bedzie Words(key=Key('Words', 5190794394730496), nom=u'jablko\n', word_form=u'jablek')
                res1 = q1.get()
                if res1 is not None:
                    q4 = Products2.query(
                        ndb.AND(
                            Products2.product == res1.nom,
                            Products2.extension == None
                        ))
                    res4 = q4.get()
                    if res4 is not None:
                        # Znalazl kategorie dla produktu zlozonego z 1 elementow
                        logging.info(q4)
                        logging.info(res4)
                        self.response.write('%s %s' % (res1.nom, res4.category))
                    else:
                        self.response.write('Produkt %s wpada do PLONK_1' % (ret))
                else:
                    # Nie ma normalizacji dla L[0] wyrazu
                    logging.info('Nie ma normalizacji dla 1 wyrazu')
                    self.response.write('Produkt %s wpada do PLONK_2' % (ret))
        else:
            # Produkt ma tylko 1 element
            q1 = Words.query().filter(Words.word_form == L[0])
            # uzywamy get() bo spodziewamy sie tylko 1 wyniku
            # pod res1 bedzie Words(key=Key('Words', 5190794394730496), nom=u'jablko\n', word_form=u'jablek')
            res1 = q1.get()
            if res1 is not None:
                q4 = Products2.query(
                    ndb.AND(
                        Products2.product == res1.nom,
                        Products2.extension == None
                    ))
                res4 = q4.get()
                if res4 is not None:
                    # Znalazl kategorie dla produktu zlozonego z 1 elementow
                    logging.info(q4)
                    logging.info(res4)
                    self.response.write('%s %s' % (res1.nom, res4.category))
                else:
                    self.response.write('Produkt %s wpada do PLONK_3' % (ret))
            else:
                # Nie ma normalizacji dla 1 wyrazu
                logging.info('Nie ma normalizacji dla 1 wyrazu')
                self.response.write('Produkt %s wpada do PLONK_4' % (ret))

    def _normalize(self, tn):
        # 0) stripowanie
        tn = tn.strip()

        # 1) same liczby wylatuja
        tn = tn.encode('utf-8').translate(None, string.digits)


        # 1a) znowu strip
        tn = tn.strip()

        # 2) wylatuja nadmiarowe spacje '  '
        tn = re.sub(' +', ' ', tn)

        # 3) usuwanie 'xspacja' i 'spacjax'
        tn = re.sub('^x ', '', tn)
        tn = re.sub(' x$', '', tn)

        # 4) wylatuja dkg
        tn = tn.replace('dkg ', '').replace(' dkg', '')

        # 5) wylatuja kg
        tn = tn.replace('kg ', '').replace(' kg', '')

        # 6) wylatuja g (gramy)
        tn = re.sub('^g ', '', tn)
        tn = re.sub(' g$', '', tn)

        prepositions = ('bez', 'w', 'na')

        # 7) zamiana (w, bez, na) spacje
        for prep in prepositions:
            tn = tn.replace(' ' + prep + ' ', ' ')

        # 8) usuwanie znakow diakrytycznych
        tn = tn.decode('utf-8')
        dicta = {u'ą': 'a',
                 u'ć': 'c',
                 u'ę': 'e',
                 u'ł': 'l',
                 u'ń': 'n',
                 u'ó': 'o',
                 u'ś': 's',
                 u'ż': 'z',
                 u'ź': 'z'}
        for el in dicta:
            tn = tn.lower().replace(el, dicta[el])

        return tn


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    (r'/update', CronUpdate),
    (r'/taskmanager', TaskManager),
    (r'/manual', Manual),
    (r'/lemmatization', Lemmatization),
    (r'/tasklemmatization', TaskLemmatization),
    (r'/stats', Statistics),
    (r'/addproducts', AddProducts),
    (r'/normalize', Normalization)
], debug=True)
