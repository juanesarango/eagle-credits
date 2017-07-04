from google.appengine.ext import ndb
from core.models import BaseModel


class Ruta(BaseModel):

    nombre = ndb.StringProperty(required=True)
    ciudad = ndb.KeyProperty()
    saldo = ndb.IntegerProperty()

    activo = ndb.BooleanProperty()
