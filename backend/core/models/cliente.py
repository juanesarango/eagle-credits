from google.appengine.ext import ndb

from core.models import BaseModel


class Cliente(BaseModel):

    # Informacion Personal
    documento = ndb.IntegerProperty(required=True)
    ruta = ndb.KeyProperty(required=True)
    nombres = ndb.StringProperty(required=True)
    apellidos = ndb.StringProperty(required=True)
    dir_casa = ndb.StringProperty()
    tel_casa = ndb.IntegerProperty()
    celular = ndb.IntegerProperty()
    imagen_documento = ndb.BlobProperty()
    imagen_negocio = ndb.BlobProperty()

    # Informacion Laboral
    nombre_est = ndb.StringProperty()
    dir_est = ndb.StringProperty()

    # Informacion Creditos
    creditos = ndb.KeyProperty(repeated=True)

    consecutivo = ndb.IntegerProperty()

    # Habilitacion
    activo = ndb.BooleanProperty()
    credito_activo = ndb.BooleanProperty()

    notas = ndb.StringProperty(repeated=True)