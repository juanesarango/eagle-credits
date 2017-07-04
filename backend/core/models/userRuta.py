from google.appengine.ext import ndb
from core.models import BaseModel


class UserRuta(BaseModel):

    ruta = ndb.KeyProperty()
    usuario = ndb.KeyProperty()