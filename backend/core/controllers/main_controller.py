from core.controllers import BaseController


class MainController(BaseController):
    def get(self):
        self.is_logged()
        self.redirect("/index")


class DownloadController(BaseController):
    def get(self):
        self.render("download.html")
