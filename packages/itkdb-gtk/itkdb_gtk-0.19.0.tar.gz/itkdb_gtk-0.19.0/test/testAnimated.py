import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GObject, Gio, GLib, GdkPixbuf




dlg = Gtk.Dialog(title="test animated", flags=0)

dlg.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.OK)

area = dlg.get_content_area()
area.set_size_request(-1, 200)


#overlay = Gtk.Overlay.new()
#area.add(overlay)

lbl = Gtk.Label(label="The Label")
area.pack_start(lbl, True, True, 0)

pxbuf = GdkPixbuf.PixbufAnimation.new_from_file("/Users/lacasta/Downloads/ezgif-3-9b8ffa642a.gif")

img = Gtk.Image.new_from_animation(pxbuf)
img.set_valign(Gtk.Align.CENTER)
img.set_halign(Gtk.Align.CENTER)
#overlay.add_overlay(img)

area.add(img)

dlg.show_all()
dlg.run()

