import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class App:
    def __init__(self):
        self.app = Gtk.Application()

    def run(self, window):
        window._gtk_window.set_application(self.app)
        self.app.connect("activate", lambda app: window._gtk_window.show_all())
        self.app.run(None)
