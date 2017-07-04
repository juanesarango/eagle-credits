from core.controllers import BaseController
from core.helpers import BaseHelper
from core.helpers import UsuarioHelper
from core.helpers import RutaHelper
from core.helpers import CreditHelper
from core.helpers import AbonoHelper
from core.helpers import TransaccionHelper
from core.helpers import ReportesHelper
from google.appengine.ext import ndb
import time
import datetime


class DepositController(BaseController):
    def get(self):
        self.is_logged()
        urlkey_ruta = self.ruta_by_role()
        rutas = RutaHelper.query_all()
        rutaSupervisor = UsuarioHelper.query_all_rutas(self.user.key)
        creditos_activos = []
        r_actual = None
        if urlkey_ruta:
            creditos_activos = CreditHelper.query_by_ruta_ayer(urlkey_ruta)
            r_actual = ndb.Key(urlsafe=urlkey_ruta).get()
        hoyutc = datetime.datetime.now() + datetime.timedelta(hours=BaseHelper.get_tzo())
        hoy = datetime.date(hoyutc.year, hoyutc.month, hoyutc.day)
        self.render("deposit.html", creditos_activos=creditos_activos, hoy=hoy,
                    r_actual=r_actual, rutas=rutas, rutaSupervisor=rutaSupervisor)

    def post(self):
        self.is_logged()
        urlkey_ruta = self.ruta_by_role()
        urlkey_credito = self.request.get("urlkey_credito")
        if self.request.get("valor"):
            valor = int(self.request.get("valor"))
            if valor <= 0:
                alert = ['alert-danger', (u'No se puede crear un abono con valor menor 0.')]
                rutas = RutaHelper.query_all()
                rutaSupervisor = UsuarioHelper.query_all_rutas(self.user.key)
                creditos_activos = []
                r_actual = None
                if urlkey_ruta:
                    creditos_activos = CreditHelper.query_by_ruta_ayer(urlkey_ruta)
                    r_actual = ndb.Key(urlsafe=urlkey_ruta).get()
                hoyutc = datetime.datetime.now() + datetime.timedelta(hours=BaseHelper.get_tzo())
                hoy = datetime.date(hoyutc.year, hoyutc.month, hoyutc.day)
                self.render("deposit.html", creditos_activos=creditos_activos, hoy=hoy, alert=alert,
                            r_actual=r_actual, rutas=rutas, rutaSupervisor=rutaSupervisor)
                return
            else:
                alert = AbonoHelper.nuevo_registro(urlkey_credito, valor, self.user.usuario)
                if alert:
                    if alert[0] == "alert-danger":
                        rutas = RutaHelper.query_all()
                        rutaSupervisor = UsuarioHelper.query_all_rutas(self.user.key)
                        creditos_activos = []
                        r_actual = None
                        if urlkey_ruta:
                            creditos_activos = CreditHelper.query_by_ruta_ayer(urlkey_ruta)
                            r_actual = ndb.Key(urlsafe=urlkey_ruta).get()
                        hoyutc = datetime.datetime.now() + datetime.timedelta(hours=BaseHelper.get_tzo())
                        hoy = datetime.date(hoyutc.year, hoyutc.month, hoyutc.day)
                        self.render("deposit.html", creditos_activos=creditos_activos, hoy=hoy, alert=alert,
                                    r_actual=r_actual, rutas=rutas, rutaSupervisor=rutaSupervisor)
                        return
                    else:
                        time.sleep(0.2)
                        self.redirect("/abono?urlkey_ruta=" + urlkey_ruta)
                time.sleep(0.2)
                self.redirect("/abono?urlkey_ruta=" + urlkey_ruta)


class ExpenseController(BaseController):
    def get(self):
        self.is_admin_supervisor()
        rutas = RutaHelper.query_all()
        rutaSupervisor = UsuarioHelper.query_all_rutas(self.user.key)
        fecha = ReportesHelper.hora_actual_mexico()
        fecha_down = datetime.datetime(fecha.year, fecha.month, fecha.day) - datetime.timedelta(days=4)
        if (self.user.role == "supervisor"):
            transacciones = TransaccionHelper.query_all_supervisor(fecha_down, rutaSupervisor)
        else:
            transacciones = TransaccionHelper.query_all(fecha_down)
        hoy = BaseHelper.limite_fecha_down()
        self.render("expense.html", rutas=rutas, transacciones=transacciones, hoy=hoy,
                    rutaSupervisor=rutaSupervisor)

    def post(self):
        self.is_logged()
        self.is_admin_supervisor()
        urlkey_ruta = self.request.get("urlkey_ruta")
        tipo = self.request.get("tipo_movimiento")
        valor = int(self.request.get("valor")) if self.request.get("valor") else None
        observacion = self.request.get("observacion")
        alert = TransaccionHelper.nuevo_registro(urlkey_ruta, valor, tipo, observacion, self.user.usuario)
        time.sleep(0.2)
        self.redirect("/gasto")


class TrasladoController(BaseController):
    def get(self):
        self.is_logged()
        self.is_admin()
        self.render("traslado.html")

    def post(self):
        self.is_logged()
        self.is_admin()
        urlkey_ruta_origen = self.request.get("urlkey_ruta_origen")
        urlkey_ruta_destino = self.request.get("urlkey_ruta_destino")
        valor = self.request.get("valor")
        if urlkey_ruta_origen and urlkey_ruta_destino and valor:
            ruta_origen = ndb.Key(urlsafe=urlkey_ruta_origen).get()
            ruta_destino = ndb.Key(urlsafe=urlkey_ruta_destino).get()
            alert = TransaccionHelper.traslado_efectivo(ruta_origen, ruta_destino, int(valor))
            self.render("traslado.html", alert=alert)
        else:
            alert = ["alert-danger", "No se pudo completar el registro"]
            self.render("traslado.html", alert=alert)


class DeleteAbonoController(BaseController):
    def post(self):
        self.is_logged()
        self.is_admin_supervisor()
        urlkey_credito = self.request.get("urlkey_credito")
        urlkey_abono = self.request.get("urlkey_abono")
        if urlkey_credito:
            abono = AbonoHelper.get_last_abono(urlkey_credito)
            if abono:
                ruta = abono.ruta
                AbonoHelper.eliminar_abono(abono)
                time.sleep(0.2)
                self.redirect("/abono?urlkey_ruta=" + ruta.urlsafe())
        elif urlkey_abono:
            abono = ndb.Key(urlsafe=urlkey_abono).get()
            if abono:
                ruta = abono.ruta
                AbonoHelper.eliminar_abono(abono)
                time.sleep(0.2)
                self.redirect("/credito?urlkey_ruta=" + ruta.urlsafe())


class DeleteTransaccionController(BaseController):
    def post(self):
        self.is_logged()
        self.is_admin_supervisor()
        urlkey_transaccion = self.request.get("urlkey_transaccion")
        if urlkey_transaccion:
            transaccion = ndb.Key(urlsafe=urlkey_transaccion).get()
            if transaccion:
                TransaccionHelper.eliminar_transaccion(transaccion)
                time.sleep(0.2)
                self.redirect("/gasto")
        self.redirect("/gasto")
