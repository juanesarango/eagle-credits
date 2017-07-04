# -*- coding: utf-8 -*-
from core.helpers import BaseHelper
from core.helpers import CreditHelper
from core.helpers import RutaHelper
from core.models import Credito
from core.models import Abono
from core.models import Consecutivo
from core.models import Transaccion
from google.appengine.ext import ndb
import datetime


class AbonoHelper(BaseHelper):
    @classmethod
    def nuevo_registro(cls, urlkey_credito, valor, usuario):
        credito_abono = ndb.Key(urlsafe=urlkey_credito).get()
        ruta_abono = credito_abono.ruta
        abono = cls.get_last_abono(urlkey_credito)
        cliente_abono = credito_abono.cliente
        if credito_abono and ruta_abono and not abono:
            if valor and valor <= credito_abono.saldo:
                con = Consecutivo.get_abono()
                a = Abono(ruta=ruta_abono, credito=credito_abono.key,
                          cliente=cliente_abono, valor=valor, consecutivo=con,
                          usuario=usuario, saldo=credito_abono.saldo - valor,
                          cuotas_faltantes=credito_abono.cuotas_faltantes - valor / float(credito_abono.valor_cuota))
                a.put()
                CreditHelper.realizar_abono(credito_abono, valor, a.key)
                RutaHelper.generar_entrada(ruta_abono.get(), valor)
                return ["alert-success", "El registro ha sido exitoso"]
            else:
                return ["alert-danger", "No se puede hacer un abono mayor al saldo del credito"]
        else:
            return ["alert-danger", "No se pudo completar el registro"]

    @classmethod
    def query_by_date(cls, fecha_up, fecha_down, urlkey_ruta):
        if urlkey_ruta:
            ruta = ndb.Key(urlsafe=urlkey_ruta)
        else:
            ruta = False
        if ruta and fecha_up and fecha_down:
            abonos = Abono.query(ndb.AND(
                Abono.creado >= fecha_down,
                Abono.creado <= fecha_up,
                Abono.ruta == ruta)).order(Abono.creado).fetch()
            return abonos
        elif fecha_up and fecha_down:
            abonos = Abono.query(ndb.AND(
                Abono.creado >= fecha_down,
                Abono.creado <= fecha_up)).order(Abono.creado).fetch()
            return abonos

    @classmethod
    def eliminar_abono(cls, abono):
        if abono:
            CreditHelper.eliminar_abono(abono)
            RutaHelper.generar_salida(abono.ruta.get(), abono.valor)
            abono.key.delete()
            return
        else:
            return

    @classmethod
    def get_last_abono(cls, urlkey_credito):
        if urlkey_credito:
            fecha_down = BaseHelper.limite_fecha_down()
            credito = ndb.Key(urlsafe=urlkey_credito).get()
            abono = Abono.query(
                ndb.AND(Abono.credito == credito.key,
                        Abono.creado >= fecha_down)).get()
            return abono
        else:
            return False


class TransaccionHelper(BaseHelper):
    @classmethod
    def nuevo_registro(cls, urlkey_ruta, valor, tipo, observacion, usuario):
        ruta = ndb.Key(urlsafe=urlkey_ruta).get()
        if ruta and valor and tipo:
            if tipo in ["EC"]:
                RutaHelper.generar_entrada(ruta, valor)
            else:
                RutaHelper.generar_salida(ruta, valor)
            t = Transaccion(ruta=ruta.key, valor=valor, tipo=tipo, observacion=observacion, usuario=usuario)
            t.put()
            return ["alert-success", "El registro ha sido exitoso"]
        else:
            return ["alert-danger", "No se pudo completar el registro"]

    @classmethod
    def query_all(cls, fecha_down):
        return Transaccion.query(ndb.AND(
            Transaccion.creado >= fecha_down,
            Transaccion.activo == True)).order(-Transaccion.creado).fetch()

    @classmethod
    def query_all_supervisor(cls, fecha_down, rutaSupervisor):
        transacciones = []
        tmp = []
        for t in rutaSupervisor:
            transa = Transaccion.query(ndb.AND(
                Transaccion.creado >= fecha_down,
                Transaccion.ruta == t.ruta,
                Transaccion.activo == True)).order(Transaccion.creado).fetch()
            if transa:
                for tra in transa:
                    tmp.append(tra)
        if tmp:
            for tra in tmp:
                if tra.tipo != u"SC" and tra.tipo != u"EC":
                    transacciones.append(tra)
        return transacciones

    @classmethod
    def query_by_date(cls, fecha_up, fecha_down, urlkey_ruta):
        if urlkey_ruta:
            ruta = ndb.Key(urlsafe=urlkey_ruta)
        else:
            ruta = False
        if ruta and fecha_up and fecha_down:
            transacciones = Transaccion.query(ndb.AND(
                Transaccion.creado >= fecha_down,
                Transaccion.creado <= fecha_up,
                Transaccion.ruta == ruta,
                Transaccion.activo == True)).order(Transaccion.creado).fetch()
            return transacciones
        elif fecha_up and fecha_down:
            transacciones = Transaccion.query(ndb.AND(
                Transaccion.creado >= fecha_down,
                Transaccion.creado <= fecha_up,
                Transaccion.activo == True)).order(Transaccion.creado).fetch()
            return transacciones

    @classmethod
    def query_by_date_supervisor(cls, fecha_up, fecha_down, urlkey_ruta):
        if urlkey_ruta:
            ruta = ndb.Key(urlsafe=urlkey_ruta)
        else:
            ruta = False
        transacciones = []
        tmp = []
        if ruta and fecha_up and fecha_down:
            transa = Transaccion.query(ndb.AND(
                Transaccion.creado >= fecha_down,
                Transaccion.creado <= fecha_up,
                Transaccion.ruta == ruta,
                Transaccion.activo == True)).order(Transaccion.creado).fetch()
            if transa:
                for tra in transa:
                    tmp.append(tra)
        elif fecha_up and fecha_down:
            transa = Transaccion.query(ndb.AND(
                Transaccion.creado >= fecha_down,
                Transaccion.creado <= fecha_up,
                Transaccion.activo == True)).order(Transaccion.creado).fetch()
            if transa:
                for tra in transa:
                    tmp.append(tra)
        if tmp:
            for tra in tmp:
                if tra.tipo != u"SC" and tra.tipo != u"EC":
                    transacciones.append(tra)
        return transacciones

    @classmethod
    def eliminar_transaccion(cls, transaccion):
        if transaccion:
            if transaccion.tipo in ["EC"]:
                RutaHelper.generar_salida(transaccion.ruta.get(), transaccion.valor)
            else:
                RutaHelper.generar_entrada(transaccion.ruta.get(), transaccion.valor)
            transaccion.activo = False
            transaccion.put()
            return

    @classmethod
    def traslado_efectivo(cls, ruta_origen, ruta_destino, valor):
        RutaHelper.generar_salida(ruta_origen, valor)
        RutaHelper.generar_entrada(ruta_destino, valor)
        return ["alert-success", "El registro ha sido exitoso"]
