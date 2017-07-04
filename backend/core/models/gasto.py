from google.appengine.ext import ndb

from core.models import BaseModel
from core.models import Ruta


class Gasto(BaseModel):

    ruta = ndb.KeyProperty(required=True, kind=Ruta)
    tipo_mov = ndb.StringProperty(required=True)
    tipo_gasto = ndb.StringProperty()
    observacion = ndb.StringProperty(required=True)

    fecha = ndb.DateProperty(required=True)
    hora = ndb.TimeProperty(required=True)
    valor = ndb.IntegerProperty(required=True)
