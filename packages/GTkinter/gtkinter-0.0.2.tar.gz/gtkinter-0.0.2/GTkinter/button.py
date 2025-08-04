import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from .enums import Events

class Button:
    def __init__(self, label):
        self._gtk_widget = Gtk.Button(label=label)

    def connect(self, event: Events, callback):
        self._gtk_widget.connect(event.value, callback)
