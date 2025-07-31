#!/home/twinkle/venv/bin/python

import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')

from gi.repository import Gtk
from gi.repository import Gdk # GDK_SELECTION_CLIPBOARD

######################################################################
# VARS

MessageType = {
     'GTK_MESSAGE_INFO': Gtk.MessageType.INFO,
  'GTK_MESSAGE_WARNING': Gtk.MessageType.WARNING,
 'GTK_MESSAGE_QUESTION': Gtk.MessageType.QUESTION,
    'GTK_MESSAGE_ERROR': Gtk.MessageType.ERROR,
    'GTK_MESSAGE_OTHER': Gtk.MessageType.OTHER,
}

ButtonType = {
      'GTK_BUTTONS_NONE': Gtk.ButtonsType.NONE,
        'GTK_BUTTONS_OK': Gtk.ButtonsType.OK,
     'GTK_BUTTONS_CLOSE': Gtk.ButtonsType.CLOSE,
    'GTK_BUTTONS_CANCEL': Gtk.ButtonsType.CANCEL,
    'GTK_BUTTONS_YES_NO': Gtk.ButtonsType.YES_NO,
 'GTK_BUTTONS_OK_CANCEL': Gtk.ButtonsType.OK_CANCEL,
}

# Message Type
GTK_MESSAGE_INFO = Gtk.MessageType.INFO
GTK_MESSAGE_WARNING = Gtk.MessageType.WARNING
GTK_MESSAGE_QUESTION = Gtk.MessageType.QUESTION
GTK_MESSAGE_ERROR = Gtk.MessageType.ERROR
GTK_MESSAGE_OTHER = Gtk.MessageType.OTHER

# Button Type
GTK_BUTTONS_NONE = Gtk.ButtonsType.NONE
GTK_BUTTONS_OK = Gtk.ButtonsType.OK
GTK_BUTTONS_CLOSE = Gtk.ButtonsType.CLOSE
GTK_BUTTONS_CANCEL = Gtk.ButtonsType.CANCEL
GTK_BUTTONS_YES_NO = Gtk.ButtonsType.YES_NO
GTK_BUTTONS_OK_CANCEL = Gtk.ButtonsType.OK_CANCEL

######################################################################
# MAIN
if __name__ == "__main__":
    print(f"[{__name__}]")
    print(__doc__)

#=====================================================================
# ALL - Make it directly accessible from the top level of the package
__all__ = ["MessageType", "ButtonType",
    "GTK_MESSAGE_INFO", "GTK_MESSAGE_WARNING", "GTK_MESSAGE_QUESTION", "GTK_MESSAGE_ERROR", "GTK_MESSAGE_OTHER",
    "GTK_BUTTONS_NONE", "GTK_BUTTONS_OK", "GTK_BUTTONS_CLOSE", "GTK_BUTTONS_CANCEL", "GTK_BUTTONS_YES_NO", "GTK_BUTTONS_OK_CANCEL",
]

""" __DATA__

__END__ """
