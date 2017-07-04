# -*- coding: utf-8 -*-
from google.appengine.ext import ndb
from core.helpers import BaseHelper
from core.models import Ruta
from core.models import Ciudad
from core.models import Caja
from core.models import User
from core.models import Abono
from core.models import Cliente
from core.models import Credito
from core.models import Transaccion
from core.models import UserRuta
from core.models import TimezoneOffset
import datetime
import logging

from core.models.stats_diarias import StatsDiarias

TimeZone = TimezoneOffset.query().get()
if TimeZone:
    TZO = TimeZone.tzo
else:
    TZO = 0

class AdminHelper(BaseHelper):
    @classmethod
    def has_children(cls, key):
        key = ndb.Key(urlsafe=key)
        kind = key.kind()
        children = 0
        if kind == 'Ciudad':
            children += Ruta.query(Ruta.ciudad == key).count()
        elif kind == 'Cliente':
            pass
        elif kind == 'Credito':
            pass
        return True if children > 0 else False

    @classmethod
    def delete(cls, key):
        key1 = ndb.Key(urlsafe=key)
        kind = key1.kind()
        cantidad = 0
        if kind != 'Ruta':
            entity = ndb.Key(urlsafe=key).get()
            entity.key.delete_async()
        elif kind == 'Ruta':
            stats = StatsDiarias.query(User.ruta == key1).fetch(200)
            cantidad += StatsDiarias.query(User.ruta == key1).count()
            if stats:
                for sta in stats:
                    sta.key.delete_async()
            transacciones = Transaccion.query(Transaccion.ruta == key1).fetch(200)
            cantidad += Transaccion.query(Transaccion.ruta == key1).count()
            if transacciones:
                for tra in transacciones:
                    tra.key.delete_async()
            abonos = Abono.query(Abono.ruta == key1).fetch(200)
            cantidad += Abono.query(Abono.ruta == key1).count()
            if abonos:
                for ab in abonos:
                    ab.key.delete_async()
            creditos = Credito.query(Credito.ruta == key1).fetch(200)
            cantidad += Credito.query(Credito.ruta == key1).count()
            if creditos:
                for cre in creditos:
                    cre.key.delete_async()
            clientes = Cliente.query(Cliente.ruta == key1).fetch(100)
            cantidad += Cliente.query(Cliente.ruta == key1).count()
            if clientes:
                for cli in clientes:
                    cli.key.delete_async()
            userRuta = UserRuta.query(UserRuta.ruta == key1).fetch()
            cantidad += UserRuta.query(UserRuta.ruta == key1).count()
            if userRuta:
                for usr in userRuta:
                    usr.key.delete_async()
            user = User.query(User.ruta == key1).fetch()
            cantidad += User.query(User.ruta == key1).count()
            if user:
                for us in user:
                    userRuta = UserRuta.query(UserRuta.usuario == us.key).fetch()
                    if not userRuta:
                        us.key.delete_async()
            print('Cantidad  = ' + str(cantidad))
            if cantidad == 0:
                key1.delete()

    @classmethod
    def get_alert(cls, code=None):
        if code:
            alert = {
                1: ['alert-danger', (u'mensaje')],
                #2: ['alert-success', mensaje],
                #3: ['alert-info', mensaje],
                #4: ['alert-warning', mensaje]
                }
            return alert[int(code)] if int(code) in alert else None
        return None

class RutaHelper(BaseHelper):

    @classmethod
    def query_all(cls, admin=False):
        if admin:
            rutas = Ruta.query().fetch()
        else:
            rutas = Ruta.query(Ruta.activo == True).fetch()
        return rutas

    @classmethod
    def existe(cls, urlkey):
        if urlkey:
            ruta_entity = ndb.Key(urlsafe=urlkey).get()
            if ruta_entity:
                return ruta_entity
            else:
                return False
        else:
            return False

    @classmethod
    def existe_nombre(cls, nombre):
        if nombre:
            if Ruta.query(Ruta.nombre == nombre).fetch():
                return True
            else:
                return False
        else:
            return False

    @classmethod
    def validar_nueva(cls, urlkey_ciudad, nombre):
        ruta_ciudad = CiudadHelper.existe(urlkey_ciudad)
        existe_nombre = cls.existe_nombre(nombre)
        if ruta_ciudad and not existe_nombre:
            return [ruta_ciudad, nombre]
        else:
            return False

    @classmethod
    def nuevo_registro(cls, urlkey_ciudad, nombre):
        ruta_params = cls.validar_nueva(urlkey_ciudad, nombre)
        if ruta_params:
            nueva_ruta = Ruta(ciudad=ruta_params[0].key,
                              nombre=ruta_params[1],
                              saldo=0,
                              activo=True)
            nueva_ruta.put()
            return ["alert-success", "El registro ha sido exitoso"]
        else:
            return ["alert-danger", "No se pudo realizar el registro"]

    @classmethod
    def generar_entrada(cls, ruta, valor):
        ruta.saldo += valor
        ruta.put()
        return

    @classmethod
    def generar_salida(cls, ruta, valor):
        ruta.saldo -= valor
        ruta.put()
        return

    @classmethod
    def get_saldo(cls, ruta):
        saldo = ruta.saldo
        return saldo

    @classmethod
    def query_all_delete(cls):
        rutas = Ruta.query(Ruta.nombre.IN(['YUCA 1', 'yuca 2', 'Caja tuxtla', 'clavos campo'])).fetch()
        return rutas

class CiudadHelper(BaseHelper):

    @classmethod
    def query_all(cls, admin=False):
        if admin:
            ciudades = Ciudad.query().fetch()
        else:
            ciudades = Ciudad.query(Ciudad.activo == True).fetch()
        return ciudades

    @classmethod
    def nuevo_registro(cls, nombre):
        if not cls.existe_nombre(nombre):
            nueva_ciudad = Ciudad(nombre=nombre)
            nueva_ciudad.put()
            return ["alert-success", "El registro ha sido exitoso"]
        else:
            return ["alert-danger", "La ciudad ya existe"]

    @classmethod
    def existe(cls, urlkey):
        if urlkey:
            ciudad_entity = ndb.Key(urlsafe=urlkey).get()
            if ciudad_entity:
                return ciudad_entity
            else:
                return False
        else:
            return False

    @classmethod
    def existe_nombre(cls, nombre):
        if nombre:
            if Ciudad.query(Ciudad.nombre == nombre).fetch():
                return True
            else:
                return False
        else:
            return False


class CajaHelper(BaseHelper):

    @classmethod
    def query_all(cls, admin=False):
        if admin:
            cajas = Caja.query().fetch()
        else:
            cajas = Caja.query(Caja.activo == True).fetch()
        return cajas

    @classmethod
    def nuevo_registro(cls, nombre):
        if not cls.existe_nombre(nombre):
            nueva_caja = Caja(nombre=nombre)
            nueva_caja.put()
            return ["alert-success", "El registro ha sido exitoso"]
        else:
            return ["alert-danger", "La Caja ya existe"]

    @classmethod
    def existe(cls, urlkey):
        if urlkey:
            caja_entity = ndb.Key(urlsafe=urlkey).get()
            if caja_entity:
                return caja_entity
            else:
                return False
        else:
            return False

    @classmethod
    def existe_nombre(cls, nombre):
        if nombre:
            if Caja.query(Caja.nombre == nombre).fetch():
                return True
            else:
                return False
        else:
            return False


class UsuarioHelper(BaseHelper):

    @classmethod
    def query_all(cls, admin=False):
        if admin:
            usuarios = User.query().fetch()
        else:
            usuarios = User.query(User.activo == True).fetch()
        return usuarios

    @classmethod
    def query_all_rutas(cls, usuario_key):
        if usuario_key:
            return UserRuta.query(UserRuta.usuario == usuario_key).fetch()
        else:
            return UserRuta.query().fetch()

    @classmethod
    def nuevo_registro(cls, documento, nombres, apellidos,
                       usuario, clave, role, rutas):
        existe_documento = cls.existe_documento(documento)
        existe_usuario = cls.existe_usuario(usuario)

        if not existe_documento and not existe_usuario and usuario and clave:
            u = User.register_ruta(documento, nombres, apellidos,
                                  usuario, clave, role)
            u.put()
            if rutas:
                for rut in rutas:
                    ruta_key = ndb.Key(urlsafe=rut)
                    rta = ruta_key.get()
                    nueva_ruta = UserRuta(ruta=rta.key, usuario=u.key)
                    nueva_ruta.put()
            return ["alert-success", "El registro ha sido exitoso"]
        else:
            return ["alert-danger", "No se pudo completar el registro"]

    @classmethod
    def existe_documento(cls, documento):
        if documento:
            if User.query(User.documento == documento).fetch():
                return True
            else:
                return False
        else:
            return False

    @classmethod
    def existe_usuario(cls, usuario):
        if usuario:
            if User.query(User.usuario == usuario).fetch():
                return True
            else:
                return False
        else:
            return False

    @classmethod
    def existe_userRuta(cls, urlkey):
        if urlkey:
            userRuta_entity = ndb.Key(urlsafe=urlkey).get()
            if userRuta_entity:
                return userRuta_entity
            else:
                return None
        else:
            return None

    @classmethod
    def actualizar_registro(cls, documento, nombres, apellidos,
                            usuario, clave, role, rutas):
        existe_documento = cls.existe_documento(documento)
        if existe_documento and usuario:
            u = User.query(User.documento == documento).get()
            u.nombres = nombres
            u.apellidos = apellidos
            if clave:
                u.clave_hash = User.make_pw_hash(usuario, clave)
            elif u.usuario != usuario and not cls.existe_usuario(usuario) and clave:
                u.clave_hash = User.make_pw_hash(usuario, clave)
                u.usuario = usuario
            u.role = role
            u.put()
            rutasEliminar = cls.query_all_rutas(u.key)
            if rutasEliminar:
                for r in rutasEliminar:
                    if r.usuario.get().usuario == u.usuario:
                        r.key.delete()
            if rutas:
                for rut in rutas:
                    ruta_key = ndb.Key(urlsafe=rut)
                    rta = ruta_key.get()
                    nueva_ruta = UserRuta(ruta=rta.key, usuario=u.key)
                    nueva_ruta.put()
            return ["alert-success", "La actualización ha sido exitoso"]
        else:
            return ["alert-danger", "No se pudo completar la actualización"]

class DepurarHelper(BaseHelper):

    @classmethod
    def depurar(cls, fecha_string):
        fecha = cls.strp2datetime(fecha_string)

        abonos = Abono.query(Abono.creado <= fecha).order(Abono.creado).fetch(100)

        creditos = Credito.query(Credito.creado <= fecha).order(Credito.creado).fetch(100)

        return abonos, creditos

    @classmethod
    def eliminarAbonos(cls, fecha_string):
        fecha = cls.strp2datetime(fecha_string)
        
        abonos = Abono.query(Abono.creado <= fecha).order(Abono.creado).fetch(1000)
        
        for abo in abonos:
            abo.key.delete()

    @classmethod
    def eliminarCreditos(cls, fecha_string):
        fecha = cls.strp2datetime(fecha_string)
        
        creditos = Credito.query(Credito.creado <= fecha).order(Credito.creado).fetch(1000)
        
        for cre in creditos:
            cre.key.delete()

    @classmethod
    def strp2datetime(cls, fecha_string):
        return datetime.datetime.strptime(str(fecha_string), "%d/%m/%Y") if fecha_string else None