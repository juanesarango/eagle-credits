import webapp2
import jinja2
import os
import datetime

from google.appengine.ext import ndb

from core.helpers import BaseHelper
from core.helpers import RutaHelper
from core.helpers import UsuarioHelper
from core.models import TimezoneOffset


template_dir = os.path.join(os.path.dirname("backend"), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)
jinja_env.filters['gmt6'] = BaseHelper.datetime_mex
jinja_env.filters['str_io_cajas'] = BaseHelper.str_io_cajas
jinja_env.filters['currency'] = BaseHelper.format_currency
jinja_env.filters['sum_stats'] = BaseHelper.sum_stats


def render_str(template, **params):
    j = jinja_env.get_template(template)
    return j.render(params)


class BaseController(webapp2.RequestHandler):

    @classmethod
    def get_tzo(cls):
        TZO = TimezoneOffset.query().get()
        if TZO:
            return TZO.tzo
        else:
            return 0

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        params['user'] = self.user
        params['rutas'] = RutaHelper.query_all()
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        cookie_val = BaseHelper.make_secure_val(val)

        if self.request.get("remember") == "yes":
            next_month = (datetime.datetime.now() + datetime.timedelta(days=30)).strftime('%a, %d %b %Y %H:%M:%S GMT')
            self.response.headers.add_header('Set-Cookie', '%s=%s; Path=/; expires= %s' % (name, cookie_val, next_month))
        else:
            tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%a, %d %b %Y %H:%M:%S GMT')
            self.response.headers.add_header('Set-Cookie', '%s=%s; Path=/; expires= %s' % (name, cookie_val, tomorrow))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and BaseHelper.check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('usi', str(user.key.urlsafe()))

    def logout(self):
        self.response.headers.add_header("Set-Cookie", "usi=; Path=/")

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        ukey = self.read_secure_cookie("usi")
        self.user = ukey and ndb.Key(urlsafe=ukey).get()

    def is_logged(self):
        if not self.user:
            self.redirect("/login", abort=True)

    def is_admin(self):
        if self.user:
            if not self.user.role == "admin":
                self.abort(401)
        else:
            self.abort(401)

    def is_admin_supervisor(self):
        if self.user:
            if self.user.role != "admin" and self.user.role != "supervisor":
                self.abort(401)
        else:
            self.abort(401)

    def ruta_by_role(self):
        if self.user:
            if self.user.role == "admin" or self.user.role == "supervisor":
                return self.request.get("urlkey_ruta")
            else:
                rutas = UsuarioHelper.query_all_rutas(self.user.key)
                if rutas:
                    for r in rutas:
                        return r.ruta.urlsafe()
                else:
                    return self.user.ruta.urlsafe()
        return None;
