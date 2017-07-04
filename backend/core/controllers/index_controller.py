from core.controllers import BaseController


class IndexController(BaseController):
    def get(self):
        self.render("index.html")
