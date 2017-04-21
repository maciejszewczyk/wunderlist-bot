from google.appengine.ext import ndb


class Note(ndb.Model):
    #req_id = ndb.IntegerProperty()      # request potrzebny do zatwierdzenia zaproszenia
    sender_id = ndb.IntegerProperty()   # kto sie z nami dzieli lista
    list_id = ndb.IntegerProperty()     # numer id listy
    revision = ndb.IntegerProperty()    # rewizja potrzebna do zaakceptowania zaproszenia
    status = ndb.IntegerProperty()      # Status dla kolejki by nie obrabiala taskow juz zrobionych
    date = ndb.DateTimeProperty(auto_now_add=True)


class Words(ndb.Model):
    word_form = ndb.StringProperty()    # forma wyrazu np. pomidory
    nom = ndb.StringProperty()          # mianownik pomidor


class Products2(ndb.Model):
    product = ndb.StringProperty()
    extension = ndb.StringProperty()
    category = ndb.StringProperty()