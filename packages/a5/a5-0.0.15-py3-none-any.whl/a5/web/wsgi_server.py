from gunicorn.app.base import BaseApplication


class _GunicornApplication(BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        for key, value in self.options.items():
            self.cfg.set(key, value)

    def load(self):
        return self.application


def run_wsgi_app(app, address, key_path=None, cert_path=None, workers=4):
    options = {"bind": address, "workers": workers, "worker_class": "sync" if workers == 1 else "gthread"}
    if key_path and cert_path:
        options["certfile"] = str(cert_path)
        options["keyfile"] = str(key_path)
    _GunicornApplication(app, options).run()
