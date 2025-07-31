import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from .event import Event

class Button:
    def __init__(self, label):
        self._gtk_widget = Gtk.Button(label=label)

    def connect(self, event: Event, callback):
        self._gtk_widget.connect(event.value, callback)
