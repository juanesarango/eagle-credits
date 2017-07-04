#!/usr/bin/env python
# -*- coding: utf-8 -*-
import webapp2
from core.controllers import MainController
from core.controllers import AdminController
from core.controllers import ClientController
from core.controllers import NewClientController
from core.controllers import ImagenDocumento
from core.controllers import ImagenNegocio
from core.controllers import CreditController
from core.controllers import NewCreditController
from core.controllers import DeleteCreditController

from core.controllers import DepositController
from core.controllers import DeleteAbonoController
from core.controllers import ExpenseController
from core.controllers import DeleteTransaccionController
from core.controllers import TrasladoController

from core.controllers import LoginController
from core.controllers import LogoutController

from core.controllers import CiudadController
from core.controllers import CajaController
from core.controllers import RutaController
from core.controllers import UsuarioController
from core.controllers import EnableController
from core.controllers import DisableController
from core.controllers import DeleteController
from core.controllers import BorrarController
from core.controllers import DepurarController
from core.controllers import DepurarAbonoController
from core.controllers import DepurarCreditoController
from core.controllers import DeleteCronController

from core.controllers import ReportesController
from core.controllers import CuadreRutaController
from core.controllers import RecaudadorAbonosController
from core.controllers import CrearStatsDiariosController
from core.controllers import ActualizarStatsDiariosController
from core.controllers import CuadreRutaResumenController
from core.controllers import RecaudadorManualController
from core.controllers import RecaudadorController
from core.controllers import GastosRutasController
from core.controllers import ClientesMoraController
from core.controllers import ClientesDiasController
from core.controllers import ClientesPuntualesController

from core.controllers import DownloadController

from core.controllers import UpdateTimeZone


app = webapp2.WSGIApplication([
    ('/', MainController),
    ('/login', LoginController),
    ('/logout', LogoutController),
    ('/index', CuadreRutaController),
    ('/admin', AdminController),
    ('/admin/ciudad', CiudadController),
    ('/admin/caja', CajaController),
    ('/admin/ruta', RutaController),
    ('/admin/usuario', UsuarioController),
    ('/admin/activar', EnableController),
    ('/admin/desactivar', DisableController),
    ('/admin/borrar', DeleteController),
    ('/admin/eliminar', BorrarController),
    ('/admin/tzo', UpdateTimeZone),
    ('/cliente', ClientController),
    ('/cliente/nuevo', NewClientController),
    ('/cliente/([^/]+)?', ClientController),
    ('/imgDoc', ImagenDocumento),
    ('/imgNeg', ImagenNegocio),
    ('/notas', ClientController),
    ('/credito', CreditController),
    ('/credito/nuevo', NewCreditController),
    ('/credito/borrar', DeleteCreditController),
    ('/abono', DepositController),
    ('/abono/borrar', DeleteAbonoController),
    ('/gasto', ExpenseController),
    ('/gasto/borrar', DeleteTransaccionController),
    ('/traslado', TrasladoController),
    ('/task/crear-stats-diarias', CrearStatsDiariosController),
    ('/task/actualizar-stats-diarias', ActualizarStatsDiariosController),
    ('/reportes', ReportesController),
    ('/reportes/cuadre-recaudador', CuadreRutaController),
    ('/reportes/cuadre-rutas', CuadreRutaResumenController),
    ('/reportes/recaudador-abonos', RecaudadorAbonosController),
    ('/reportes/recaudador-manual', RecaudadorManualController),
    ('/reportes/recaudador', RecaudadorController),
    ('/reportes/gastos-rutas', GastosRutasController),
    ('/reportes/clientes-mora', ClientesMoraController),
    ('/reportes/client_expired', ClientesDiasController),
    ('/reportes/client_good', ClientesPuntualesController),
    ('/depurar', DepurarController),
    ('/depurar/abono', DepurarAbonoController),
    ('/depurar/credito', DepurarCreditoController),
    ('/download', DownloadController),
    ('/task/deleteRutas', DeleteCronController)

], debug=True)

