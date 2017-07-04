from google.appengine.ext import ndb

from core.models import BaseModel


class Credito(BaseModel):

    cliente = ndb.KeyProperty(required=True)
    nombres = ndb.StringProperty()
    ruta = ndb.KeyProperty(required=True)
    valor = ndb.IntegerProperty(required=True)
    tasa = ndb.IntegerProperty()
    fecha_cre = ndb.DateProperty()
    dias = ndb.IntegerProperty()
    fecha_ven = ndb.DateProperty()
    consecutivo = ndb.IntegerProperty()

    credito = ndb.IntegerProperty()
    saldo = ndb.IntegerProperty()
    valor_cuota = ndb.IntegerProperty()
    cuotas_faltantes = ndb.FloatProperty()

    # Informacion Pagos/Abonos
    abonos = ndb.KeyProperty(repeated=True)
    num_cuota = ndb.IntegerProperty()

    estado = ndb.StringProperty()
    fecha_ult_pago = ndb.DateProperty()
    ultima_cuota = ndb.IntegerProperty()

    activo = ndb.BooleanProperty()

    usuario = ndb.StringProperty()

    # Numeracion de la tarjeta
    codigo = ndb.StringProperty()