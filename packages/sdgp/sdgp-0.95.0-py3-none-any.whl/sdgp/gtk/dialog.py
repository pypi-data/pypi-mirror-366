#!/home/twinkle/venv/bin/python
# -*- encoding: utf-8 -*-

import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')

from gi.repository import Gtk
from gi.repository import Gdk # GDK_SELECTION_CLIPBOARD

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
# CLASS

def dialog(dtext='Nothing.', label='label', title='dialog', dtype=GTK_MESSAGE_INFO, btype=GTK_BUTTONS_OK):

    if dtype == GTK_MESSAGE_ERROR:
        print(f"{__name__}: {dtext}\n")
    else:
        print(f"{__name__}: {dtext}\n")

    dialog = Gtk.MessageDialog(
                               transient_for=Gtk.Window(),
                               flags=Gtk.DialogFlags.MODAL,
                               message_type=dtype,
                               buttons=btype,
                               text=label
                               )

    dialog.set_default_size(320, 256)
    dialog.set_title("sd-get-prompt")
    dialog.set_skip_taskbar_hint(False);
    dialog.set_position(Gtk.WindowPosition.CENTER);
    dialog.format_secondary_text(dtext);

    # メッセージエリア内のGtkLabelを取得し、選択可能にする
    # GtkMessageDialog.get_message_area() は GtkBox を返す
    # その GtkBox の子ウィジェットが GtkLabel
    message_area = dialog.get_message_area()
    # GtkMessageDialog のメッセージラベルは、通常、message_area の最初の子（主メッセージ）です
    for child in message_area.get_children():
        if isinstance(child, Gtk.Label):
            child.set_selectable(True)
            #break # 最初に見つかったGtkLabelだけを対象とする場合

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
    "dialog", "GTK_MESSAGE_INFO", "GTK_MESSAGE_WARNING", "GTK_MESSAGE_QUESTION", "GTK_MESSAGE_ERROR", "GTK_MESSAGE_OTHER",
    "GTK_BUTTONS_NONE", "GTK_BUTTONS_OK", "GTK_BUTTONS_CLOSE", "GTK_BUTTONS_CANCEL", "GTK_BUTTONS_YES_NO", "GTK_BUTTONS_OK_CANCEL",
]

""" __DATA__

__END__ """
