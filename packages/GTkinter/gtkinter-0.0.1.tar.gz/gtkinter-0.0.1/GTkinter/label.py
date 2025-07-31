import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class Label:
    def __init__(self, text):
        self._gtk_widget = Gtk.Label(label=text)

    def set_text(self, text):
        self._gtk_widget.set_text(text)
