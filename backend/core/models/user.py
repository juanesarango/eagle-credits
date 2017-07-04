from google.appengine.ext import ndb
from core.models import BaseModel
import random
import hashlib
from string import letters


class User(BaseModel):

    ruta = ndb.KeyProperty()
    documento = ndb.IntegerProperty()
    nombres = ndb.StringProperty()
    apellidos = ndb.StringProperty()
    direccion = ndb.StringProperty()
    usuario = ndb.StringProperty(required=True)
    clave_hash = ndb.StringProperty(required=True)
    role = ndb.StringProperty()
    activo = ndb.BooleanProperty()

    @classmethod
    def register(cls, documento, nombres, apellidos,
                 usuario, clave, role):

        clave_hash = cls.make_pw_hash(usuario, clave)

        return User(documento=documento, nombres=nombres,
                    apellidos=apellidos,
                    usuario=usuario, clave_hash=clave_hash, role=role)

    @classmethod
    def register_ruta(cls, documento, nombres, apellidos,
                 usuario, clave, role):

        clave_hash = cls.make_pw_hash(usuario, clave)

        return User(documento=documento, nombres=nombres,
                    apellidos=apellidos,
                    usuario=usuario, clave_hash=clave_hash, role=role)

    @classmethod
    def register_fast(cls, usuario, clave):
        clave_hash = cls.make_pw_hash(usuario, clave)
        return User(usuario=usuario, clave_hash=clave_hash, role="admin")

    @classmethod
    def login(cls, usuario, clave):
        u = cls.query(cls.usuario == usuario).get()
        if u and cls.valid_pw(usuario, clave, u.clave_hash):
            return u

    @classmethod
    def make_salt(cls, length=7):
        return ''.join(random.choice(letters) for x in xrange(length))

    @classmethod
    def make_pw_hash(cls, name, pw, salt=None):
        if not salt:
            salt = cls.make_salt()
        h = hashlib.sha256(name + pw + salt).hexdigest()
        return '%s,%s' % (salt, h)

    @classmethod
    def valid_pw(cls, name, password, h):
        salt = h.split(',')[0]
        return h == cls.make_pw_hash(name, password, salt)
