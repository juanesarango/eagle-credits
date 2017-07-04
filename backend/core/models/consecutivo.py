from google.appengine.ext import ndb

from core.models import BaseModel


class Consecutivo(BaseModel):

    cliente = ndb.IntegerProperty()
    credito = ndb.IntegerProperty()
    abono = ndb.IntegerProperty()

    @classmethod
    def get_cliente(cls):
        con = Consecutivo.query().fetch()
        if not con:
            c = Consecutivo(cliente=2, credito=1, abono=1)
            c.put()
            return 1
        else:
            c = con[0].cliente
            con[0].cliente += 1
            con[0].put()
            return c

    @classmethod
    def get_credito(cls):
        con = Consecutivo.query().fetch()
        if not con:
            c = Consecutivo(cliente=1, credito=2, abono=1)
            c.put()
            return 1
        else:
            c = con[0].credito
            con[0].credito += 1
            con[0].put()
            return c

    @classmethod
    def get_abono(cls):
        con = Consecutivo.query().fetch()
        if not con:
            c = Consecutivo(cliente=1, credito=1, abono=2)
            c.put()
            return 1
        else:
            c = con[0].abono
            con[0].abono += 1
            con[0].put()
            return c
