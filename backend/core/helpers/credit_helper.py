# -*- coding: utf-8 -*-
from core.helpers import BaseHelper
from core.helpers import RutaHelper
from core.helpers import ClientHelper
#from core.helpers import AbonoHelper
from core.models import Credito
from core.models import Consecutivo
from core.models import Abono
from google.appengine.ext import ndb
import datetime
import logging


class CreditHelper(BaseHelper):

    @classmethod
    def nuevo_registro(cls, codigo, urlkey_cliente, valor, tasa, fecha_cre_str, dias, fecha_ven_str, usuario, abono):
        cliente = ndb.Key(urlsafe=urlkey_cliente).get()
        ruta = cliente.ruta
        credito = valor*tasa/100+valor
        saldo = credito
        valor_cuota = credito/dias
        con = Consecutivo.get_credito()

        if cliente and credito and fecha_cre_str and valor_cuota:
            fecha_cre = datetime.datetime.strptime(str(fecha_cre_str), "%d/%m/%Y")
            fecha_ven = datetime.datetime.strptime(str(fecha_ven_str), "%d/%m/%Y")
            nuevo_credito = Credito(codigo=codigo, cliente=cliente.key,
                                    nombres=cliente.nombres,
                                    ruta=ruta, valor=valor,
                                    tasa=tasa, fecha_cre=fecha_cre, dias=dias,
                                    fecha_ven=fecha_ven, consecutivo=con,
                                    credito=credito, saldo=saldo,
                                    valor_cuota=valor_cuota, num_cuota=0,
                                    cuotas_faltantes=dias, estado="A",
                                    activo=True, usuario=usuario)
            nuevo_credito.put()
            ClientHelper.asignar_credito(cliente.key, nuevo_credito)
            if abono > 0:
                cls.primer_abono(nuevo_credito, abono, usuario)
            RutaHelper.generar_salida(ruta.get(), valor)
            return ["alert-success", "El registro ha sido exitoso"]
        else:
            return ["alert-danger", "No se pudo completar el registro"]

    @classmethod
    def primer_abono(cls, credito_abono, valor, usuario):
        ruta_abono = credito_abono.ruta
        cliente_abono = credito_abono.cliente
        if credito_abono and ruta_abono and valor >= 0:
            con = Consecutivo.get_abono()
            a = Abono(ruta=ruta_abono, credito=credito_abono.key,
                      cliente=cliente_abono, valor=valor, consecutivo=con,
                      usuario=usuario)
            a.put()
            cls.realizar_abono(credito_abono, valor, a.key)
            RutaHelper.generar_entrada(ruta_abono.get(), valor)
            return ["alert-success", "El registro ha sido exitoso"]
        else:
            return ["alert-danger", "No se pudo completar el registro"]

    @classmethod
    def eliminar_credito(cls, urlkey_credito):
        credito = ndb.Key(urlsafe=urlkey_credito).get()
        if credito:
            ClientHelper.eliminar_credito(credito)
            RutaHelper.generar_entrada(credito.ruta.get(), credito.valor)
            credito.key.delete()
            return

    @classmethod
    def query_all(cls, admin=False):
        if admin:
            creditos = Credito.query().fetch()
        else:
            creditos = Credito.query(Credito.estado == "A").fetch()
        return creditos

    @classmethod
    def query_by_ruta(cls, urlkey_ruta):
        ruta_key = ndb.Key(urlsafe=urlkey_ruta)
        return Credito.query(ndb.AND(
            Credito.ruta == ruta_key,
            Credito.estado == "A",
            Credito.activo == True)).order(Credito.creado).fetch()

    @classmethod
    def query_by_ruta_dias(cls, urlkey_ruta, hoy):
        creditos = []
        ruta_key = ndb.Key(urlsafe=urlkey_ruta)
        tmp = Credito.query(ndb.AND(
            Credito.ruta == ruta_key,
            Credito.estado == "A",
            Credito.activo == True)).order(Credito.creado).fetch()
        if tmp:
            for cre in tmp:
                if (hoy.date() - cre.creado.date()).days > 24:
                    creditos.append(cre)
        return creditos

    @classmethod
    def query_by_ruta_puntuales(cls, urlkey_ruta, estado, hoy):
        creditos = []
        ruta_key = ndb.Key(urlsafe=urlkey_ruta)
        clientes = ClientHelper.query_by_ruta(urlkey_ruta, True)
        if clientes:
            for cli in clientes:
                if estado == "P":
                    #tmp = Credito.query(ndb.AND(Credito.ruta == ruta_key,Credito.estado == "P")).order(Credito.creado).fetch()
                    tmp = Credito.query(ndb.AND(
                        Credito.cliente == cli.key,
                        Credito.ruta == ruta_key,
                        Credito.estado == "P")).order(-Credito.creado).fetch(1)
                else:
                    #tmp = Credito.query(ndb.AND(Credito.ruta == ruta_key,Credito.estado == "A")).order(Credito.creado).fetch()
                    tmp = Credito.query(ndb.AND(
                        Credito.cliente == cli.key,
                        Credito.ruta == ruta_key,
                        Credito.estado == "A")).order(-Credito.creado).fetch(1)
                if tmp:
                    if tmp[0].saldo <= 0:
                        if tmp[0].estado == "P":
                            if (tmp[0].fecha_ult_pago - tmp[0].creado.date()).days < 24:
                                    creditos.append(tmp[0])
                        else:
                            if (hoy.date() - tmp[0].creado.date()).days < 24:
                                creditos.append(tmp[0])
        return creditos

    @classmethod
    def query_by_ruta_ayer(cls, urlkey_ruta):
        ruta_key = ndb.Key(urlsafe=urlkey_ruta)
        fecha_down = cls.limites_fecha()[0]
        return Credito.query(ndb.AND(
            Credito.ruta == ruta_key,
            Credito.estado == "A",
            Credito.activo == True,
            Credito.creado <= fecha_down)).order(Credito.creado).fetch()

    @classmethod
    def query_activos(cls):
        return Credito.query(Credito.estado == "A").fetch()

    @classmethod
    def realizar_abono(cls, credito_a_abonar, valor, abono_key):
        credito_a_abonar.saldo -= valor
        credito_a_abonar.cuotas_faltantes -= valor/float(credito_a_abonar.valor_cuota)
        credito_a_abonar.fecha_ult_pago = datetime.datetime.now() + datetime.timedelta(hours=cls.get_tzo())
        credito_a_abonar.abonos.append(abono_key)
        credito_a_abonar.num_cuota += 1
        credito_a_abonar.ultima_cuota = valor
        if credito_a_abonar.saldo <= 0:
            ClientHelper.credito_finalizado(credito_a_abonar.cliente)
            credito_a_abonar.saldo = 0
            credito_a_abonar.cuotas_faltantes = 0
            credito_a_abonar.activo = False
            credito_a_abonar.estado = "P"
        credito_a_abonar.put()
        return

    @classmethod
    def query_by_date(cls, fecha_up, fecha_down, urlkey_ruta):
        if urlkey_ruta:
            ruta = ndb.Key(urlsafe=urlkey_ruta)
        else:
            ruta = False
        if ruta and fecha_up and fecha_down:
            creditos = Credito.query(ndb.AND(
                Credito.creado >= fecha_down,
                Credito.creado <= fecha_up,
                Credito.estado == "A",
                Credito.ruta == ruta)).order(Credito.creado).fetch()
            return creditos
        elif fecha_up and fecha_down:
            creditos = Credito.query(ndb.AND(
                Credito.creado >= fecha_down,
                Credito.creado <= fecha_up,
                Credito.estado == "A")).order(Credito.creado).fetch()
            return creditos

    @classmethod
    def query_clientes_mora(cls):
        antier = datetime.datetime.now() + datetime.timedelta(days=-2)
        return Credito.query(ndb.AND(Credito.fecha_ult_pago == None,
                                     Credito.creado <= antier)).order(Credito.creado).fetch()

    @classmethod
    def eliminar_abono(cls, abono):
        credito = abono.credito.get()
        credito.saldo += abono.valor
        credito.cuotas_faltantes += abono.valor/float(credito.valor_cuota)
        credito.fecha_ult_pago = BaseHelper.hora_actual_mexico() - datetime.timedelta(days=1)
        credito.abonos.remove(abono.key)
        credito.num_cuota -= 1
        credito.put()
        return

    @classmethod
    def query_by_client(cls, urlkey_client):
        cliente = ndb.Key(urlsafe=urlkey_client)
        if cliente:
            return Credito.query(Credito.cliente == cliente).order(Credito.creado).fetch()
        else:
            return []

    @classmethod
    def query_by_client_ultimo(cls, urlkey_client):
        cliente = ndb.Key(urlsafe=urlkey_client)
        if cliente:
            return Credito.query(Credito.cliente == cliente).order(-Credito.creado).fetch(1)
        else:
            return []

    @classmethod
    def nueva_nota(cls, urlkey_client, nota):
        cliente = ndb.Key(urlsafe=urlkey_client).get()
        if cliente:
            cliente.notas.append(nota)
            cliente.put()