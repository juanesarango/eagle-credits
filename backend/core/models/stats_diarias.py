from google.appengine.ext import ndb
from core.models import BaseModel


class StatsDiarias(BaseModel):

    ruta = ndb.KeyProperty()
    fecha = ndb. DateProperty()
    abonos = ndb.IntegerProperty()
    creditos = ndb.IntegerProperty()
    gastos = ndb.IntegerProperty()
    sueldos = ndb.IntegerProperty()
    entradas = ndb.IntegerProperty()
    salidas = ndb.IntegerProperty()
    caja_anterior = ndb.IntegerProperty()
    saldo = ndb.IntegerProperty()
    porcentaje_abonos = ndb.IntegerProperty()
    total = ndb.IntegerProperty()
    clientes = ndb.IntegerProperty()
    salidas_socio = ndb.IntegerProperty()
    cuota = ndb.IntegerProperty()
