from core.controllers import BaseController
from core.helpers import RutaHelper
from core.helpers import ClientHelper
from core.helpers import UsuarioHelper
from core.helpers import CreditHelper
from core.helpers import ReportesHelper
from google.appengine.ext import ndb
import time


class CreditController(BaseController):
    def get(self):
        self.is_logged()
        urlkey_ruta = self.ruta_by_role()
        creditos = []
        r_actual = None
        rutaSupervisor = UsuarioHelper.query_all_rutas(self.user.key)
        if urlkey_ruta:
            creditos = CreditHelper.query_by_ruta(urlkey_ruta)
            r_actual = ndb.Key(urlsafe=urlkey_ruta).get()
        hoy = ReportesHelper.limite_fecha_down()
        self.render("credit.html", creditos=creditos, r_actual=r_actual, hoy=hoy,
                    rutaSupervisor=rutaSupervisor)

    def post(self):
        self.is_logged()
        key = self.request.get('key')
        credito = ndb.Key(urlsafe=key).get()
        abonos = [abono.get() for abono in credito.abonos]
        urlkey_ruta = self.ruta_by_role()
        rutas = RutaHelper.query_all()
        rutaSupervisor = UsuarioHelper.query_all_rutas(self.user.key)
        if urlkey_ruta:
            creditos = CreditHelper.query_by_ruta(urlkey_ruta)
            r_actual = ndb.Key(urlsafe=urlkey_ruta).get()
        else:
            creditos = CreditHelper.query_all()
            r_actual = False
        hoy = ReportesHelper.limite_fecha_down()
        self.render("credit.html", creditos=creditos, rutas=rutas,
                    rutaSupervisor=rutaSupervisor, r_actual=r_actual, abonos=abonos, c_actual=credito,
                    hoy=hoy)


class NewCreditController(BaseController):
    def get(self):
        self.is_logged()
        if self.user.role == "admin" or self.user.role == "supervisor":
            urlkey_ruta = self.request.get("urlkey_ruta")
            if urlkey_ruta:
                clientes = ClientHelper.query_by_ruta(urlkey_ruta, True)
            else:
                clientes = ClientHelper.query_all(True)
        else:
            if self.user.ruta:
                ruta_empleado = self.user.ruta.urlsafe()
            else:
                ruta_empleado = UsuarioHelper.query_all_rutas(self.user.key)[0].ruta.urlsafe()
            clientes = ClientHelper.query_by_ruta(ruta_empleado, True)
        self.render("new_credit.html", clientes=clientes)

    def post(self):
        self.is_logged()

        cliente = self.request.get("urlkey_cliente")
        valor = int(self.request.get("valor")) if self.request.get("valor") else None
        tasa = int(self.request.get("tasa")) if self.request.get("tasa") else None
        fecha_cre = self.request.get("fecha_cre")
        dias = int(self.request.get("dias")) if self.request.get("dias") else None
        fecha_ven = self.request.get("fecha_ven")
        str_abono = self.request.get("abono")
        codigo = self.request.get("codigo")
        if str_abono:
            abono = int(str_abono)
        else:
            abono = 0
        cliente_entity = ndb.Key(urlsafe=cliente).get()
        if not cliente_entity.credito_activo:
            alert = CreditHelper.nuevo_registro(codigo, cliente, valor, tasa, fecha_cre, dias, fecha_ven,
                                                self.user.usuario, abono)
        else:
            if self.user.role == "admin" or self.user.role == "supervisor":
                urlkey_ruta = self.request.get("urlkey_ruta")
                if urlkey_ruta:
                    clientes = ClientHelper.query_by_ruta(urlkey_ruta, True)
                else:
                    clientes = ClientHelper.query_all(True)
            else:
                if self.user.ruta:
                    ruta_empleado = self.user.ruta.urlsafe()
                else:
                    ruta_empleado = UsuarioHelper.query_all_rutas(self.user.key)[0].ruta.urlsafe()
                clientes = ClientHelper.query_by_ruta(ruta_empleado, True)
            alert = ['alert-danger', 'El cliente actual cuenta con un credito activo!']
            self.render("new_credit.html", alert=alert, clientes=clientes)
        time.sleep(0.2)
        self.redirect("/credito")


class DeleteCreditController(BaseController):
    def post(self):
        urlkey_credito = self.request.get("urlkey_credito")
        if urlkey_credito:
            CreditHelper.eliminar_credito(urlkey_credito)
            self.redirect("/credito")
