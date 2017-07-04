from google.appengine.ext import ndb

from core.models import BaseModel
from core.models import Ruta
from core.models import Credito
from core.models import Cliente


class Abono(BaseModel):

    ruta = ndb.KeyProperty(required=True, kind=Ruta)
    credito = ndb.KeyProperty(required=True, kind=Credito)
    cliente = ndb.KeyProperty(required=True, kind=Cliente)
    usuario = ndb.StringProperty()
    valor = ndb.IntegerProperty(required=True)
    consecutivo = ndb.IntegerProperty()

    saldo = ndb.IntegerProperty()
    cuotas_faltantes = ndb.FloatProperty()