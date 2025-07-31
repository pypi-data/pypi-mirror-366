import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from .event import Event

class Window:
    def __init__(self, title="SimpleGTK Window", width=400, height=300):
        self._gtk_widget = Gtk.Window()
        self._gtk_widget.set_title(title)
        self._gtk_widget.set_default_size(width, height)

    def set_child(self, widget):
        self._gtk_widget.add(widget._gtk_widget)

    def connect(self, event: Event, callback):
        self._gtk_widget.connect(event.value, callback)