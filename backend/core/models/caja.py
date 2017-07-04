from google.appengine.ext import ndb
from core.models import BaseModel


class Caja(BaseModel):

    nombre = ndb.StringProperty(required=True)
    saldo = ndb.IntegerProperty()
