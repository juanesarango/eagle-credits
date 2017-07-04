# -*- coding: utf-8 -*-
from core.helpers import BaseHelper
from core.helpers import CreditHelper
from core.helpers import RutaHelper
from core.helpers import UsuarioHelper
from core.helpers import AbonoHelper
from core.helpers import TransaccionHelper
from core.models import Credito
from core.models import Abono
from core.models import Consecutivo
from core.models import Transaccion
from core.models import StatsDiarias
from core.models import TimezoneOffset
from google.appengine.ext import ndb
import datetime
import logging

TimeZone = TimezoneOffset.query().get()
# logging.info(TimeZone)
if TimeZone:
    TZO = TimeZone.tzo
else:
    TZO = 0


class ReportesHelper(BaseHelper):
    @classmethod
    def cuadre_ruta_fecha(cls, fecha_string, urlkey_ruta, params, supervisor):
        fecha = cls.strp2datetime(fecha_string)
        fecha_down, fecha_up, = cls.limites_fecha(fecha)
        abonos = cls.stats_abonos(fecha_up, fecha_down, urlkey_ruta, params)[1]
        creditos = cls.stats_creditos(fecha_up, fecha_down, urlkey_ruta, params)[1]
        transacciones = cls.stats_transacciones_super(fecha_up, fecha_down, urlkey_ruta, params, supervisor)[1]
        params = cls.saldo_rutas(urlkey_ruta, params)
        params['rutas'] = RutaHelper.query_all()
        cls.actualizar_stats_diarias()
        ruta = ndb.Key(urlsafe=urlkey_ruta).get()
        if ruta:
            stats = cls.stats_diarias_by_ruta(fecha_string, fecha_string, ruta)
            if stats:
                params['caja_anterior'] = stats[0].caja_anterior
                params['total_abonos'] = stats[0].abonos
                params['total_creditos'] = stats[0].creditos
                params['total_entradas'] = stats[0].entradas
                params['total_salidas'] = stats[0].salidas
                params['total_gastos'] = stats[0].gastos
                params['total_sueldos'] = stats[0].sueldos
                params['total_salida_socio'] = stats[0].salidas_socio
                params['saldo_total'] = stats[0].total
                params['total_cuota'] = stats[0].cuota
                params['porcentaje_abonos'] = stats[0].porcentaje_abonos
                params['total_clientes'] = stats[0].clientes

                # params['caja_anterior'] = params['saldo_total'] -\
                # params['total_abonos'] +\
                # params['total_creditos'] -\
                # params['total_entradas'] +\
                # params['total_salidas']
        return abonos, creditos, transacciones, params

    @classmethod
    def gastos_rutas(cls, fecha_down_str, fecha_up_str, ruta=None):
        movimientos = []
        params = dict(
            total_entradas=0,
            total_salida_socio=0,
            total_salidas=0,
            total_gastos=0,
            total_sueldos=0)
        if fecha_down_str and fecha_up_str:
            fecha_down = cls.limite_fecha_down(
                cls.strp2datetime(fecha_down_str))
            fecha_up = cls.limites_fecha_up(
                cls.strp2datetime(fecha_up_str))
            if ruta:
                movimientos.append(
                    cls.stats_transacciones(
                        fecha_up, fecha_down, ruta.key.urlsafe(), params)[1])
                return movimientos
            else:
                rutas = RutaHelper.query_all()
                if rutas:
                    for r in rutas:
                        mov = cls.stats_transacciones(fecha_up,fecha_down,r.key.urlsafe(),params)[1]
                        if mov:
                            movimientos.append(mov)
                return movimientos
        else:
            return movimientos

    @classmethod
    def gastos_rutas_supervisor(cls, fecha_down_str, fecha_up_str, rutaSupervisor, usuario_key):
        movimientos = []
        if fecha_down_str and fecha_up_str:
            fecha_down = cls.limite_fecha_down(cls.strp2datetime(fecha_down_str))
            fecha_up = cls.limites_fecha_up(cls.strp2datetime(fecha_up_str))
            if rutaSupervisor:
                for ruta in rutaSupervisor:
                    mov = cls.stats_transacciones_supervisor(fecha_up,fecha_down,ruta.ruta.get().key.urlsafe())
                    if mov:
                        movimientos.append(mov)
                return movimientos
            else:
                rutas = UsuarioHelper.query_all_rutas(usuario_key)
                if rutas:
                    for r in rutas:
                        mov = cls.stats_transacciones_supervisor(fecha_up,fecha_down,r.key.urlsafe())
                        if mov:
                            movimientos.append(mov)
                return movimientos
        else:
            return movimientos

    @classmethod
    def clientes_mora(cls):
        creditos = CreditHelper.query_clientes_mora()
        return creditos

    @classmethod
    def cuadre_rutas(cls, fecha_down_str=None, fecha_up_str=None,
                     ruta=None, role=None, usuario_key=None):
        stats = []
        if fecha_down_str and fecha_up_str:
            if ruta:
                stats.append(cls.stats_diarias_by_ruta(fecha_down_str,
                                                       fecha_up_str,
                                                       ruta))
                return stats
            else:
                if role == "supervisor":
                    stats = cls.stats_diarias_all_rutas_supervisor(fecha_down_str,fecha_up_str, usuario_key)
                else:
                    stats = cls.stats_diarias_all_rutas(fecha_down_str,fecha_up_str)
                return stats
        else:
            return stats

    @classmethod
    def stats_diarias_all_rutas(cls, fecha_down_str, fecha_up_str):
        stats = []
        rutas = RutaHelper.query_all()
        if rutas:
            for r in rutas:
                sta = cls.stats_diarias_by_ruta(fecha_down_str,fecha_up_str,r)
                if sta:
                    stats.append(sta)
        return stats

    @classmethod
    def stats_diarias_all_rutas_supervisor(cls, fecha_down_str, fecha_up_str, usuario_key):
        stats = []
        rutas = UsuarioHelper.query_all_rutas(usuario_key)
        if rutas:
            for r in rutas:
                sta = cls.stats_diarias_by_ruta(fecha_down_str,fecha_up_str,r.ruta.get())
                if sta:
                    stats.append(sta)
        return stats

    @classmethod
    def stats_diarias_by_ruta(cls, fecha_down_str, fecha_up_str, ruta):
        fecha_down = cls.datetime2date(cls.strp2datetime(fecha_down_str))
        fecha_up = cls.datetime2date(cls.strp2datetime(fecha_up_str))
        return StatsDiarias.query(
            ndb.AND(StatsDiarias.fecha >= fecha_down,
                    StatsDiarias.fecha <= fecha_up,
                    StatsDiarias.ruta == ruta.key)).fetch()

    @classmethod
    def crear_stats_diarias(cls):
        fecha = cls.fecha_actual()
        rutas = RutaHelper.query_all()
        for r in rutas:
            s = StatsDiarias.query(ndb.AND(StatsDiarias.ruta == r.key,
                                           StatsDiarias.fecha == fecha)).get()
            if not s:
                stats = StatsDiarias(fecha=fecha,
                                     ruta=r.key,
                                     caja_anterior=r.saldo,
                                     abonos=0,
                                     creditos=0,
                                     gastos=0,
                                     sueldos=0,
                                     entradas=0,
                                     salidas=0,
                                     saldo=0,
                                     porcentaje_abonos=0,
                                     total=0,
                                     clientes=0,
                                     salidas_socio=0,
                                     cuota=0)
                stats.put()

    @classmethod
    def actualizar_stats_diarias(cls, fecha=None):
        if not fecha:
            fecha = cls.fecha_actual()
        fecha_down, fecha_up = cls.limites_fecha(fecha)
        rutas = RutaHelper.query_all()
        crear = False
        for r in rutas:
            params = dict(
                total_abonos=0,
                total_creditos=0,
                total_gastos=0,
                total_sueldos=0,
                total_salida_socio=0,
                total_entradas=0,
                total_salidas=0,
                total_cuota=0,
                clientes_abonaron=0,
                total_clientes=0,
                saldo_total=0,
                saldo=0)
            stats = StatsDiarias.query(ndb.AND(StatsDiarias.ruta == r.key,
                                               StatsDiarias.fecha >= cls.datetime2date(fecha_down),
                                               StatsDiarias.fecha <= cls.datetime2date(fecha_up))).get()
            params = cls.query_stats_by_ruta(fecha_up, fecha_down, r.key.urlsafe(), params)[0]
            if stats:
                stats.abonos = params['total_abonos']
                stats.creditos = params['total_creditos']
                stats.gastos = params['total_gastos']
                stats.sueldos = params['total_sueldos']
                stats.entradas = params['total_entradas']
                stats.salidas = params['total_salidas']
                stats.salidas_socio = params['total_salida_socio']
                stats.saldo = params['saldo']
                stats.cuota = params['total_cuota']
                stats.clientes = params['total_clientes']
                if params['total_cuota'] > 0:
                    stats.porcentaje_abonos = params['total_abonos'] * 100 / params['total_cuota']
                else:
                    stats.porcentaje_abonos = 0
                if not stats.caja_anterior or stats.caja_anterior == 0:
                    stats.caja_anterior = r.saldo - params['total_abonos'] + params['total_creditos'] - params['total_entradas'] + params['total_salidas']
                stats.total = r.saldo
                stats.put()
            else:
                porcentajeAbonos = 0
                if params['total_cuota'] > 0:
                    porcentajeAbonos = params['total_abonos'] * 100 / params['total_cuota']

                stats = StatsDiarias(fecha=fecha,
                                     ruta=r.key,
                                     caja_anterior=r.saldo - params['total_abonos'] + params['total_creditos'] - params['total_entradas'] + params['total_salidas'],
                                     abonos=params['total_abonos'],
                                     creditos=params['total_creditos'],
                                     gastos=params['total_gastos'],
                                     sueldos=params['total_sueldos'],
                                     entradas=params['total_entradas'],
                                     salidas=params['total_salidas'],
                                     saldo=params['saldo'],
                                     porcentaje_abonos=porcentajeAbonos,
                                     total=r.saldo,
                                     clientes=params['total_clientes'],
                                     salidas_socio=params['total_salida_socio'],
                                     cuota=params['total_cuota'])
                stats.put()

    @classmethod
    def inactivar_creditos_finalizados(cls):
        creditos = Credito.query(Credito.saldo <= 0).fetch()
        for c in creditos:
            c.estado = "P"
            c.activo = False
            c.put()
        return

    @classmethod
    def query_stats_by_ruta(cls, fecha_up, fecha_down, urlkey_ruta, params):
        params, abonos = cls.stats_abonos(fecha_up, fecha_down, urlkey_ruta,
                                          params)
        params, creditos = cls.stats_creditos(fecha_up, fecha_down,
                                              urlkey_ruta, params)
        params, transacciones = cls.stats_transacciones(fecha_up, fecha_down,
                                                        urlkey_ruta, params)
        return params, abonos, creditos, transacciones

    @classmethod
    def stats_abonos(cls, fecha_up, fecha_down, urlkey_ruta, params):
        abonos = AbonoHelper.query_by_date(fecha_up, fecha_down, urlkey_ruta)
        if abonos:
            for a in abonos:
                params['total_abonos'] += a.valor
            params['clientes_abonaron'] = len(abonos)
        return params, abonos

    @classmethod
    def stats_creditos(cls, fecha_up, fecha_down, urlkey_ruta, params):
        creditos = CreditHelper.query_by_date(fecha_up, fecha_down, urlkey_ruta)
        params['total_creditos'] = 0
        params['total_cuota'] = 0
        if creditos:
            for c in creditos:
                params['total_creditos'] += c.valor
        if urlkey_ruta:
            creditos_activos = CreditHelper.query_by_ruta_ayer(urlkey_ruta)
        else:
            creditos_activos = CreditHelper.query_activos()

        if creditos_activos:
            for c in creditos_activos:
                params['total_cuota'] += c.valor_cuota
                params['saldo'] += c.saldo
            params['total_clientes'] = len(creditos_activos)
        return params, creditos

    @classmethod
    def stats_transacciones_super(cls, fecha_up, fecha_down, urlkey_ruta, params, supervisor):
        if supervisor:
            transacciones = TransaccionHelper.query_by_date_supervisor(fecha_up, fecha_down, urlkey_ruta)
        else:
            transacciones = TransaccionHelper.query_by_date(fecha_up, fecha_down, urlkey_ruta)
        if transacciones:
            for t in transacciones:
                if t.tipo == "EC":
                    params['total_entradas'] += t.valor
                elif t.tipo == "SC":
                    params['total_salidas'] += t.valor
                elif t.tipo == "GA":
                    params['total_gastos'] += t.valor
                elif t.tipo == "SS":
                    params['total_salida_socio'] += t.valor
                elif t.tipo == "SU":
                    params['total_sueldos'] += t.valor

        return params, transacciones

    @classmethod
    def stats_transacciones(cls, fecha_up, fecha_down, urlkey_ruta, params):
        transacciones = TransaccionHelper.query_by_date(fecha_up, fecha_down,
                                                        urlkey_ruta)
        if transacciones:
            for t in transacciones:
                if t.tipo == "EC":
                    params['total_entradas'] += t.valor
                elif t.tipo == "SC":
                    params['total_salidas'] += t.valor
                elif t.tipo == "GA":
                    params['total_gastos'] += t.valor
                elif t.tipo == "SS":
                    params['total_salida_socio'] += t.valor
                elif t.tipo == "SU":
                    params['total_sueldos'] += t.valor

        return params, transacciones

    @classmethod
    def stats_transacciones_supervisor(cls, fecha_up, fecha_down, urlkey_ruta):
        transacciones = TransaccionHelper.query_by_date_supervisor(fecha_up, fecha_down, urlkey_ruta)
        return transacciones

    @classmethod
    def saldo_rutas(cls, urlkey_ruta, params):
        if urlkey_ruta:
            ruta = ndb.Key(urlsafe=urlkey_ruta).get()
        else:
            ruta = False

        if ruta:
            params['saldo_total'] = RutaHelper.get_saldo(ruta)
            return params
        else:
            rutas = RutaHelper.query_all()
            for r in rutas:
                params['saldo_total'] += RutaHelper.get_saldo(r)
            return params

    @classmethod
    def limites_fecha(cls, fecha=None, utc=TZO):
        if not fecha:
            fecha = cls.hora_actual_mexico()
        fecha_up = datetime.datetime(fecha.year, fecha.month, fecha.day, 23, 59) + datetime.timedelta(hours=-utc)
        fecha_down = datetime.datetime(fecha.year, fecha.month, fecha.day) + datetime.timedelta(hours=-utc)
        return fecha_down, fecha_up

    @classmethod
    def limite_fecha_down(cls, fecha=None, tzo=TZO):
        if not fecha:
            fecha = cls.hora_actual_mexico()
        return datetime.datetime(fecha.year, fecha.month, fecha.day) + datetime.timedelta(hours=-tzo)

    @classmethod
    def limites_fecha_up(cls, fecha=None, tzo=TZO):
        if not fecha:
            fecha = cls.hora_actual_mexico()
        return datetime.datetime(fecha.year, fecha.month, fecha.day, 23, 59) + datetime.timedelta(hours=-tzo)

    @classmethod
    def strp2datetime(cls, fecha_string):
        return datetime.datetime.strptime(str(fecha_string), "%d/%m/%Y") if fecha_string else None

    @classmethod
    def datetime2date(cls, fecha=None):
        return datetime.date(fecha.year, fecha.month, fecha.day) if fecha else None

    def query_abonos_9dias(cls, fecha_str, urlkey_ruta=None):
        fecha = cls.strp2datetime(fecha_str) if fecha_str else cls.hora_actual_mexico()
        lim_fechas = [ReportesHelper().limites_fecha(fecha + datetime.timedelta(days=i)) for i in xrange(0, 9)]
        abonos = []
        fechas = []
        if urlkey_ruta:
            for down, up in lim_fechas:
                abonos.append(Abono.query(ndb.AND(
                                          Abono.ruta == ndb.Key(urlsafe=urlkey_ruta), 
                                          Abono.creado > down,
                                          Abono.creado < up)).fetch())
                fechas.append(down)
        else:
            for down, up in lim_fechas:
                abonos.append(Abono.query(ndb.AND(Abono.creado > down, Abono.creado < up)).fetch())
                fechas.append(down)
        return abonos, fechas

    @classmethod
    def query_creditos(cls, urlkey_ruta):
        creditos = []
        tmp = Credito.query(Credito.ruta == ndb.Key(urlsafe=urlkey_ruta)).order(Credito.fecha_ult_pago).fetch()
        if tmp:
            for cre in tmp:
                if cre.saldo > 0:
                    creditos.append(cre)
        return creditos

    @classmethod
    def fecha_actual(cls, tzo=TZO):
        fecha = datetime.datetime.now() + datetime.timedelta(hours=tzo)
        fecha_act = datetime.date(fecha.year, fecha.month, fecha.day)
        return fecha_act

    @classmethod
    def hora_actual_mexico(cls):
        return datetime.datetime.now() + datetime.timedelta(hours=TZO)
