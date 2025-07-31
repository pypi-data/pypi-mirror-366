#!/home/twinkle/venv/bin/python
# -*- encoding: utf-8 -*-

import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')

from gi.repository import Gtk
from gi.repository import Gdk # GDK_SELECTION_CLIPBOARD
from gi.repository import Pango

######################################################################
# VARS

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
# DEFS

def txview(dtext='Nothing.', label='label', title='dialog', dtype=GTK_MESSAGE_INFO, btype=GTK_BUTTONS_OK):

    def on_close(fixed, widget):
        widget.close()

    if dtype == GTK_MESSAGE_ERROR:
        print(f"{__name__}: {dtext}\n")
    else:
        print(f"{__name__}: {dtext}\n")

    gwin = Gtk.Window()

    dialog = Gtk.Dialog(
               title=title,
               transient_for=gwin,
               flags=Gtk.DialogFlags.MODAL,
               )

    dialog.set_default_size(384, 512)
    dialog.set_skip_taskbar_hint(False);
    dialog.set_position(Gtk.WindowPosition.CENTER);

    box = dialog.get_content_area()

    attr = Pango.AttrList()
    attr.insert(Pango.attr_foreground_new(65535, 0, 0))
    attr.insert(Pango.attr_size_new(Pango.SCALE * 48))
    attr.insert(Pango.attr_family_new('Serif'))

    lbl1 = Gtk.Label(label, attr)
    lbl1.set_markup(f"<big><b>{label}</b></big>")
    lbl1.set_margin_top(6)
    lbl1.set_margin_bottom(6)
    box.add(lbl1)

    # GtkTextView を作成し、テキストをセット
    textview = Gtk.TextView()
    textbuffer = textview.get_buffer()
    textbuffer.set_text(dtext)

    # 読み取り専用にする
    textview.set_editable(True)
    textview.set_wrap_mode(True)
    textview.set_cursor_visible(True) # カーソルを非表示に
    textview.set_left_margin(4)
    textview.set_right_margin(4)
    textview.set_top_margin(4)
    textview.set_bottom_margin(4)

    # スクロール可能にするために GtkScrolledWindow に入れる
    scrolled_window = Gtk.ScrolledWindow()
    scrolled_window.set_vexpand(True)
    scrolled_window.set_hexpand(False)
    scrolled_window.add(textview)

    box.pack_start(scrolled_window, True, True, 2)

    btn1 = Gtk.Button("CLOSE")
    btn1.connect("clicked", on_close, dialog)
    box.add(btn1)
    dialog.show_all()

    retv = dialog.run()

    # クリップボードオブジェクトを取得
    clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
    # クリップボードの内容を永続化（ストア）
    # これにより、アプリケーションが終了してもクリップボードの内容が保持されます
    clipboard.store()

    dialog.destroy()
    # ^^;
    return retv

######################################################################
# MAIN
if __name__ == "__main__":
    print(f"[{__name__}]")
    print(__doc__)

#=====================================================================
# ALL - Make it directly accessible from the top level of the package
__all__ = [
    "txview", "GTK_MESSAGE_INFO", "GTK_MESSAGE_WARNING", "GTK_MESSAGE_QUESTION", "GTK_MESSAGE_ERROR", "GTK_MESSAGE_OTHER",
    "GTK_BUTTONS_NONE", "GTK_BUTTONS_OK", "GTK_BUTTONS_CLOSE", "GTK_BUTTONS_CANCEL", "GTK_BUTTONS_YES_NO", "GTK_BUTTONS_OK_CANCEL",
]

""" __DATA__

__END__ """
