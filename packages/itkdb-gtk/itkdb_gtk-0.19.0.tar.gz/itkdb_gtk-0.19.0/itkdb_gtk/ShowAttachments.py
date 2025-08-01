import sys
from pathlib import Path

try:
    import itkdb_gtk
    
except ImportError:
    from pathlib import Path
    cwd = Path(__file__).parent.parent
    sys.path.append(cwd.as_posix())

from itkdb_gtk import dbGtkUtils, ITkDButils

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio, Gdk


def add_attachment_dialog():
    """Create the add attachment dialog."""
    dlg = Gtk.Dialog(title="Add Attachment")
    dlg.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                    Gtk.STOCK_OK, Gtk.ResponseType.OK)
    grid = Gtk.Grid(column_spacing=5, row_spacing=1)
    box = dlg.get_content_area()
    box.add(grid)

    lbl = Gtk.Label(label="File")
    lbl.set_xalign(0)
    grid.attach(lbl, 0, 0, 1, 1)

    lbl = Gtk.Label(label="Title")
    lbl.set_xalign(0)
    grid.attach(lbl, 0, 1, 1, 1)

    lbl = Gtk.Label(label="Description")
    lbl.set_xalign(0)
    grid.attach(lbl, 0, 2, 1, 1)

    dlg.fC = Gtk.FileChooserButton()
    grid.attach(dlg.fC, 1, 0, 1, 1)

    dlg.att_title = Gtk.Entry()
    grid.attach(dlg.att_title, 1, 1, 1, 1)

    dlg.att_desc = Gtk.Entry()
    grid.attach(dlg.att_desc, 1, 2, 1, 1)

    dlg.show_all()
    return dlg


class ShowAttachments(Gtk.Dialog):
    """Window to show attachments."""
    def __init__(self, title, session, attachments=[], parent=None):
        """Initialization."""
        super().__init__(title=title, transient_for=parent)
        self.session = session
        self.attachments = [A for A in attachments]
        self.init_window()

    def init_window(self):
        """Prepares the window."""
        self.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                         Gtk.STOCK_OK, Gtk.ResponseType.OK)

        self.mainBox = self.get_content_area()
        # The "Add attachment" button.
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.mainBox.pack_start(box, False, False, 0)

        dbGtkUtils.add_button_to_container(box, "Add attachment",
                                           "Click to add a new attachment.",
                                           self.add_attachment)

        dbGtkUtils.add_button_to_container(box, "Remove attachment",
                                           "Click to remove selected attachment.",
                                           self.remove_attachment)

        # the list of attachments
        tree_view = self.create_tree_view()
        self.mainBox.pack_start(tree_view, True, True, 0)
        for A in self.attachments:
            self.append_attachment_to_view(A)

        self.show_all()

    def create_tree_view(self, size=150):
        """Creates the tree vew with the attachments."""
        model = Gtk.ListStore(str, str, str, str)
        self.tree = Gtk.TreeView(model=model)
        self.tree.connect("button-press-event", self.button_pressed)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.add(self.tree)
        scrolled.set_size_request(-1, size)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Attachment", renderer, text=0)
        self.tree.append_column(column)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Title", renderer, text=1)
        self.tree.append_column(column)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Description", renderer, text=2)
        self.tree.append_column(column)

        return scrolled

    def button_pressed(self, tree, event):
        """Button clicked on top of attachment."""
        # double click shows attachments
        it = None
        model = self.tree.get_model()
        if event.button == 1 and event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS:
            select = self.tree.get_selection()
            model, it = select.get_selected()
            if not it:
                return

            self.edit_attachment(model, it)
            return

        if event.button != 3:
            return

        # Create popup menu
        select = self.tree.get_selection()
        model, it = select.get_selected()
        values = None
        if it:
            values = model[it]

        else:
            P = tree.get_path_at_pos(event.x, event.y)
            if P:
                it = model.get_iter(P[0])
                values = model[it]

        if not values:
            return

        if not it:
            P = self.tree.get_path_at_pos(event.x, event.y)
            if P:
                it = model.get_iter(P[0])

        if not it:
            return

        menu = Gtk.Menu()
        item_edit = Gtk.MenuItem(label="Edit")
        item_edit.connect("activate", self.on_edit_attachment, (model, it))
        menu.append(item_edit)

        item_show = Gtk.MenuItem(label="Show file")
        item_show.connect("activate", self.on_show_file, (model, it))
        menu.append(item_show)

        menu.show_all()
        menu.popup_at_pointer(event)

    def edit_attachment(self, model, it):
        """Edit attachment at current row."""
        values = model[it]
        dlg = add_attachment_dialog()
        dlg.fC.set_filename(values[3])
        dlg.att_title.set_text(values[1])
        dlg.att_desc.set_text(values[2])
        rc = dlg.run()
        if rc == Gtk.ResponseType.OK:
            path = Path(dlg.fC.get_filename())
            title = dlg.att_title.get_text()
            desc = dlg.att_desc.get_text()
            model.set_value(it, 0, path.name)
            model.set_value(it, 1, title)
            model.set_value(it, 2, desc)
            model.set_value(it, 3, path.as_posix())

        dlg.hide()
        dlg.destroy()

    def on_edit_attachment(self, item, data):
        """Test JSon."""
        model, it = data
        self.edit_attachment(model, it)


    def on_show_file(self, item, data):
        """Test JSon."""
        model, it  = data
        values = model[it]
        sss = None
        try:
            with open(values[3], "tr", encoding="utf-8") as f:
                sss = f.read()
        
        except UnicodeDecodeError:
            dbGtkUtils.complain("Error showing file", "File is not a text file")
            return        
        
        
        dlg = Gtk.Dialog(title="Add Attachment",
                     transient_for=self,
                     flags=0)
        dlg.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.OK)
        dlg.set_size_request(300, 200)
        area = dlg.get_content_area()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        area.add(box)

        scrolledwindow = Gtk.ScrolledWindow()
        box.pack_start(scrolledwindow, False, True, 0)

        scrolledwindow.set_hexpand(True)
        scrolledwindow.set_vexpand(True)
        textview = Gtk.TextView()
        textview.get_buffer().set_text(sss)
        scrolledwindow.add(textview)
        dlg.show_all()
        dlg.run()
        dlg.hide()
        dlg.destroy()
        

    def add_attachment(self, *args):
        """Add Attachment button clicked."""
        dlg = add_attachment_dialog()
        rc = dlg.run()
        if rc == Gtk.ResponseType.OK:
            path = Path(dlg.fC.get_filename())
            A = ITkDButils.Attachment(path=path, 
                                      title=dlg.att_title.get_text().strip(), 
                                      desc=dlg.att_desc.get_text().strip())
            self.append_attachment_to_view(A)
            self.attachments.append(A)

        dlg.hide()
        dlg.destroy()

    def append_attachment_to_view(self, A):
        """Insert attachment to tree view."""
        model = self.tree.get_model()
        model.append([A.path.name, A.title, A.desc, A.path.as_posix()])

    def remove_attachment(self, *args):
        """Remove selected attachment."""
        select = self.tree.get_selection()
        model, it = select.get_selected()
        if it:
            values = model[it]
            for a in self.attachments:
                if a.path == values[3]:
                    rc = dbGtkUtils.ask_for_confirmation("Remove this attachment ?",
                                                         "{} - {}\n{}".format(a.title, a.desc, values[0]))
                    if rc:
                        self.attachments.remove(a)
                        model.remove(it)

                    break

if __name__ == "__main__":
    SA = ShowAttachments("Test Attachments", None)
    SA.run()
