# -*- coding: utf-8 -*-
from core.helpers import BaseHelper
from core.models import Cliente
from core.models import Consecutivo
from admin_helper import RutaHelper
from google.appengine.ext import ndb
import datetime


class ClientHelper(BaseHelper):

    @classmethod
    def query_all(cls, filtro=False):
        if filtro:
            return Cliente.query(Cliente.credito_activo == False).order(Cliente.nombres).fetch()
        else:
            return Cliente.query().order(Cliente.nombres).fetch()

    @classmethod
    def query_by_ruta(cls, urlkey_ruta, filtro=False):
        ruta_key = ndb.Key(urlsafe=urlkey_ruta)
        if filtro:
            return Cliente.query(ndb.AND(Cliente.ruta == ruta_key, 
                                Cliente.credito_activo == False)).order(Cliente.nombres).fetch()
        else:
            return Cliente.query(Cliente.ruta == ruta_key).order(Cliente.nombres).fetch()

    @classmethod
    def nuevo_registro(cls, documento, ruta, nombres, apellidos, dir_casa,
                       tel_casa, celular, nombre_est, dir_est, imagen_documento, imagen_negocio):
        existe_ruta = RutaHelper.existe(ruta)
        existe_documento = cls.existe_documento(documento)
        if existe_ruta and not existe_documento and documento and nombres and apellidos:
            con = Consecutivo.get_cliente()
            nuevo_cliente = Cliente(documento=documento, ruta=existe_ruta.key,
                                    nombres=nombres, apellidos=apellidos,
                                    dir_casa=dir_casa, tel_casa=tel_casa,
                                    celular=celular, nombre_est=nombre_est,
                                    dir_est=dir_est, consecutivo=con,
                                    credito_activo=False, imagen_documento=imagen_documento,
                                    imagen_negocio=imagen_negocio)
            nuevo_cliente.put()
            return ["alert-success", "El registro ha sido exitoso"]
        else:
            return ["alert-danger", "No se pudo completar el registro"]

    @classmethod
    def actualizar_registro(cls, cliente_key, documento, ruta, nombres, apellidos, dir_casa,
                            tel_casa, celular, nombre_est, dir_est, imagen_documento, imagen_negocio):
        existe_ruta = RutaHelper.existe(ruta)
        cliente = cliente_key.get()
        if cliente:
            cliente.documento = documento
            cliente.ruta = existe_ruta.key
            cliente.nombres = nombres
            cliente.apellidos = apellidos
            cliente.dir_casa = dir_casa
            cliente.tel_casa = tel_casa
            cliente.celular = celular
            cliente.nombre_est = nombre_est
            cliente.dir_est = dir_est
            if imagen_documento:
                cliente.imagen_documento = imagen_documento
            if imagen_negocio:
                cliente.imagen_negocio = imagen_negocio
            cliente.put()
            return ["alert-success", "La actualización ha sido exitoso"]
        else:
            return ["alert-danger", "No se pudo completar la actualización"]

    @classmethod
    def existe_documento(cls, documento):
        if documento:
            if Cliente.query(Cliente.documento == documento).fetch():
                return True
            else:
                return False
        else:
            return False

    @classmethod
    def asignar_credito(cls, key_cliente, key_credito):
        cliente = key_cliente.get()
        cliente.creditos.append(key_credito.key)
        cliente.credito_activo = True
        cliente.put()
        return

    @classmethod
    def eliminar_credito(cls, credito):
        cliente = credito.cliente.get()
        cliente.creditos.remove(credito.key)
        cliente.credito_activo = False
        cliente.put()

    @classmethod
    def credito_finalizado(cls, key_cliente):
        cliente = key_cliente.get()
        cliente.credito_activo = False
        cliente.put()
        return
