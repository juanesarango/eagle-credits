# -*- coding: utf-8 -*-
import hmac
import re
import datetime
from core.models import TimezoneOffset
thing = "ZaoZvf4ml3Sgn5VRsEa5gsYf4oblrku49KGwRDzn"


class BaseHelper(object):

    @classmethod
    def get_tzo(cls):
        TZO = TimezoneOffset.query().get()
        if TZO:
            return TZO.tzo
        else:
            return 0

    @classmethod
    def make_secure_val(cls, val):
        return '%s|%s' % (val, hmac.new(thing, val).hexdigest())

    @classmethod
    def check_secure_val(cls, secure_val):
        val = secure_val.split('|')[0]
        if secure_val == cls.make_secure_val(val):
            return val

    @classmethod
    def valid_string(cls, s, a, b):
        S_RE = re.compile(r"^.{3,30}$")
        return s and S_RE.match(s)

    @classmethod
    def valid_number(cls, n, a, b):
        N_RE = re.compile(r"^[0-9]{3,15}$")
        return n and N_RE.match(n)

    @classmethod
    def valid_mail(cls, mail):
        MAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
        return not mail or MAIL_RE.match(mail)

    @classmethod
    def datetime_mex(cls, hora):
        return hora + datetime.timedelta(hours=cls.get_tzo()) if hora else None

    @classmethod
    def str_io_cajas(cls, tipo):
        tipo_string = dict(
            EC="Entrada Efectivo",
            SC="Salida Efectivo",
            GA="Gastos",
            SS="Salida Socio",
            SU="Sueldo")
        return tipo_string[tipo]

    @classmethod
    def limites_fecha(cls, fecha=None):
        utc = cls.get_tzo()
        if not fecha:
            fecha = cls.hora_actual_mexico()
        fecha_up = datetime.datetime(fecha.year, fecha.month, fecha.day, 23, 59) + datetime.timedelta(hours=-utc)
        fecha_down = datetime.datetime(fecha.year, fecha.month, fecha.day) + datetime.timedelta(hours=-utc)
        return fecha_down, fecha_up

    @classmethod
    def limite_fecha_down(cls, fecha=None):
        tzo = cls.get_tzo()
        if not fecha:
            fecha = cls.hora_actual_mexico()
        return datetime.datetime(fecha.year, fecha.month, fecha.day) + datetime.timedelta(hours=-tzo)

    @classmethod
    def hora_actual_mexico(cls):
        tzo = cls.get_tzo()
        return datetime.datetime.now() + datetime.timedelta(hours=tzo)

    @classmethod
    def format_currency(cls, value):
        if value is None:
            value = 0
        return "${:,.0f}".format(value)

    @classmethod
    def sum_stats(cls, stats, at):
        suma = 0
        if at == "abonos":
            for s in stats:
                suma += s.abonos
            return suma
        elif at == "creditos":
            for s in stats:
                suma += s.creditos
            return suma
        elif at == "gastos":
            for s in stats:
                suma += s.gastos
            return suma
        elif at == "sueldos":
            for s in stats:
                suma += s.sueldos
            return suma
        elif at == "entradas":
            for s in stats:
                suma += s.entradas
            return suma
        elif at == "salidas":
            for s in stats:
                suma += s.salidas
            return suma
        elif at == "salidas_socio":
            for s in stats:
                suma += s.salidas_socio
            return suma
