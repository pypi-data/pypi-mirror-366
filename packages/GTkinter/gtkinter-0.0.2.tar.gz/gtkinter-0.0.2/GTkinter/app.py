import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class App:
    def __init__(self):
        self.app = Gtk.Application()
        self._window = None

    def run(self, window):
        self._window = window

        def on_activate(app):
            gtk_win = self._window._gtk_widget
            gtk_win.set_application(app)
            gtk_win.show_all()

        self.app.connect("activate", on_activate)
        self.app.run(None)
