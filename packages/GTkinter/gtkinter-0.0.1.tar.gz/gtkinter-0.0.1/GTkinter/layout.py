import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class VBox:
    def __init__(self, spacing=10):
        self._gtk_widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=spacing)

    def add(self, widget):
        self._gtk_widget.pack_start(widget._gtk_widget, True, True, 0)

class HBox:
    def __init__(self, spacing=10):
        self._gtk_widget = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=spacing)

    def add(self, widget):
        self._gtk_widget.pack_start(widget._gtk_widget, True, True, 0)
