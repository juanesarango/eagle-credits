from google.appengine.ext import ndb
from core.models import BaseModel


class Ciudad(BaseModel):

    nombre = ndb.StringProperty(required=True)
    activo = ndb.BooleanProperty()
