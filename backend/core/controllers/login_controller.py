# -*- coding: utf-8 -*-
from core.controllers import BaseController
from core.models import User


class LoginController(BaseController):
    def get(self):
        self.render("login.html")

    def post(self):
        login = self.request.get("login")
        clave = self.request.get("clave")

        u = User.login(login, clave)
        if u:
            self.login(u)
            self.redirect("/")
        else:
            msg_error = u'El usuario o contraseña es inválido'
            self.render("login.html", msg_error=msg_error)
            return


class LogoutController(BaseController):
    def get(self):
        self.logout()
        self.redirect("/")
        return
