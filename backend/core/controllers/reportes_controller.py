from core.controllers import BaseController
from core.helpers import ReportesHelper
from core.helpers import RutaHelper
from core.helpers import UsuarioHelper
from core.helpers import CreditHelper
from google.appengine.ext import ndb
import datetime
import logging


class ReportesController(BaseController):
    def get(self):
        self.is_logged()
        self.is_admin_supervisor()
        self.render("lista_reportes.html")

class CuadreRutaController(BaseController):
    def get(self):
        self.is_logged()
        fecha_str = self.request.get("fecha_str")
        urlkey_ruta = self.ruta_by_role()
        rutas = RutaHelper.query_all()
        rutaSupervisor = UsuarioHelper.query_all_rutas(self.user.key)
        params = dict(
                total_abonos=0,
                total_creditos=0,
                total_entradas=0,
                total_salidas=0,
                total_gastos=0,
                total_sueldos=0,
                total_salida_socio=0,
                total_cuota=0,
                clientes_abonaron=0,
                total_clientes=0,
                saldo_total=0,
                saldo=0,
                porcentaje_abonos=0,
                caja_anterior=0)
        if urlkey_ruta and fecha_str:
            if self.user.role == "supervisor":
                abonos, creditos, transacciones, params = ReportesHelper.cuadre_ruta_fecha(
                                            fecha_str, urlkey_ruta, params, True)
            else:
                abonos, creditos, transacciones, params = ReportesHelper.cuadre_ruta_fecha(
                                            fecha_str, urlkey_ruta, params, False)
            if urlkey_ruta:
                ruta = ndb.Key(urlsafe=urlkey_ruta).get()
                if ruta:
                    r_actual = ruta.nombre
            else:
                r_actual = False
            self.render("cuadre_ruta.html",
                        abonos=abonos,
                        creditos=creditos,
                        transacciones=transacciones,
                        r_actual=r_actual,
                        rutaSupervisor=rutaSupervisor,
                        **params)
        else:
            self.render("cuadre_ruta.html", rutas=rutas, rutaSupervisor=rutaSupervisor, r_actual=None,
             **params)

class RecaudadorAbonosController(BaseController):
    def get(self):
        fecha_str = self.request.get("fecha_str")
        urlkey_ruta = self.ruta_by_role()
        if urlkey_ruta:
            creditos = ReportesHelper().query_creditos(urlkey_ruta)
            abonos, fechas = ReportesHelper().query_abonos_9dias(fecha_str, urlkey_ruta)
            ruta = ndb.Key(urlsafe=urlkey_ruta).get()
            if ruta:
                r_actual = ruta.nombre
        else:
            creditos = CreditHelper().query_all()
            abonos, fechas = ReportesHelper().query_abonos_9dias(fecha_str)
            r_actual = False
        rutaSupervisor = UsuarioHelper.query_all_rutas(self.user.key)
        self.render("recaudador-abonos.html",
                    abonos=abonos,
                    creditos=creditos,
                    fechas=fechas,
                    r_actual=r_actual,
                    rutaSupervisor=rutaSupervisor
                    )


class RecaudadorManualController(BaseController):
    def get(self):
        fecha_str = self.request.get("fecha_str")
        num_dias = int(self.request.get("num_dias")) if self.request.get("num_dias") else 5
        urlkey_ruta = self.ruta_by_role()
        fecha = ReportesHelper.strp2datetime(fecha_str) if fecha_str else ReportesHelper.hora_actual_mexico()
        fechas = [ReportesHelper.limites_fecha(fecha + datetime.timedelta(days=i))[0] for i in xrange(0, num_dias)]
        if urlkey_ruta:
            creditos = ReportesHelper().query_creditos(urlkey_ruta)
            ruta = ndb.Key(urlsafe=urlkey_ruta).get()
            if ruta:
                r_actual = ruta.nombre
        else:
            creditos = CreditHelper().query_all()
            r_actual = False
        rutaSupervisor = UsuarioHelper.query_all_rutas(self.user.key)
        self.render("recaudador-manual.html",
                    creditos=creditos,
                    fechas=fechas,
                    num_dias=num_dias,
                    r_actual=r_actual,
                    rutaSupervisor=rutaSupervisor
                    )


class RecaudadorController(BaseController):
    def get(self):
        urlkey_ruta = self.ruta_by_role()
        if urlkey_ruta:
            creditos = ReportesHelper().query_creditos(urlkey_ruta)
            ruta = ndb.Key(urlsafe=urlkey_ruta).get()
            if ruta:
                r_actual = ruta.nombre
        else:
            creditos = CreditHelper().query_all()
            r_actual = False
        rutaSupervisor = UsuarioHelper.query_all_rutas(self.user.key)
        self.render("recaudador.html",
                    creditos=creditos,
                    r_actual=r_actual,
                    rutaSupervisor=rutaSupervisor
                    )


class CuadreRutaResumenController(BaseController):
    def get(self):
        self.is_logged()
        self.is_admin_supervisor()
        rutas = RutaHelper.query_all()
        rutaSupervisor = UsuarioHelper.query_all_rutas(self.user.key)
        urlkey_ruta = self.request.get('urlkey_ruta')
        ruta = None
        fecha_down_str = self.request.get('fecha_down_str')
        fecha_up_str = self.request.get('fecha_up_str')
        if urlkey_ruta:
            ruta = ndb.Key(urlsafe=urlkey_ruta).get()
            if ruta:
                r_actual = ruta.nombre
        else:
            r_actual = None
        stats = ReportesHelper.cuadre_rutas(fecha_down_str, fecha_up_str,
                                            ruta if ruta else None, self.user.role, self.user.key)
        self.render("cuadre_rutas.html", stats=stats, rutas=rutas, rutaSupervisor=rutaSupervisor,
                     r_actual=r_actual)


class GastosRutasController(BaseController):
    def get(self):
        self.is_logged()
        self.is_admin_supervisor()
        urlkey_ruta = self.request.get('urlkey_ruta')
        fecha_down_str = self.request.get('fecha_down_str')
        fecha_up_str = self.request.get('fecha_up_str')
        ruta = None
        if urlkey_ruta:
            ruta = ndb.Key(urlsafe=urlkey_ruta).get()
        movimientos = ReportesHelper.gastos_rutas(fecha_down_str,
                                                  fecha_up_str,
                                                  ruta)
        rutaSupervisor = UsuarioHelper.query_all_rutas(self.user.key)
        movimientos_supervisor = ReportesHelper.gastos_rutas_supervisor(fecha_down_str,
                                                      fecha_up_str,
                                                      rutaSupervisor, self.user.key)
        self.render("gastos_rutas.html", movimientos_rutas=movimientos, rutaSupervisor=rutaSupervisor,
                    movimientos_rutas_supervisor=movimientos_supervisor, ruta=ruta if ruta else None)

class ClientesMoraController(BaseController):
    def get(self):
        self.is_logged()
        self.is_admin_supervisor()
        creditos = ReportesHelper.clientes_mora()
        self.render("clientes_mora.html", creditos=creditos)

class ClientesDiasController(BaseController):
    def get(self):
        self.is_logged()
        self.is_admin_supervisor()
        urlkey_ruta = self.ruta_by_role()
        r_actual = False
        creditos = []
        abonos = []
        hoy = ReportesHelper.limite_fecha_down()
        if urlkey_ruta:
            creditos = CreditHelper.query_by_ruta_dias(urlkey_ruta, hoy)
            r_actual = ndb.Key(urlsafe=urlkey_ruta).get()
        rutas = RutaHelper.query_all()
        rutaSupervisor = UsuarioHelper.query_all_rutas(self.user.key)
        self.render("client_expired.html", creditos=creditos, rutas=rutas, r_actual=r_actual, 
                    rutaSupervisor=rutaSupervisor, hoy=hoy)
        return

class ClientesPuntualesController(BaseController):
    def get(self):
        self.is_logged()
        self.is_admin()
        urlkey_ruta = self.ruta_by_role()
        estado = self.request.get('estado')
        r_actual = False
        creditos = []
        abonos = []
        hoy = ReportesHelper.limite_fecha_down()
        if urlkey_ruta:
            creditos = CreditHelper.query_by_ruta_puntuales(urlkey_ruta, estado, hoy)
            r_actual = ndb.Key(urlsafe=urlkey_ruta).get()
        rutas = RutaHelper.query_all()
        rutaSupervisor = UsuarioHelper.query_all_rutas(self.user.key)
        self.render("client_good.html", creditos=creditos, rutas=rutas, r_actual=r_actual, 
                    rutaSupervisor=rutaSupervisor, hoy=hoy)
        return

class CrearStatsDiariosController(BaseController):
    def get(self):
        ReportesHelper.crear_stats_diarias()


class ActualizarStatsDiariosController(BaseController):
    def get(self):
        ReportesHelper.actualizar_stats_diarias()
        ReportesHelper.inactivar_creditos_finalizados()
