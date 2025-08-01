
try:
    import itkdb_gtk
    
except ImportError:
    import sys
    from pathlib import Path
    cwd = Path(__file__).parent.parent
    sys.path.append(cwd.as_posix())

from itkdb_gtk import dbGtkUtils

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio, Gdk


class ShowDefects(Gtk.Dialog):
    """Edit defects"""
    
    def __init__(self, title, defects=None, parent=None):
        """Initialization."""
        super().__init__(title=title, transient_for=parent)
        if defects:
            self.defects = [C for C in defects]
        else:
            self.defects = []
            
        self.init_window()

    def init_window(self):
        """Preapare the window."""
        self.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                         Gtk.STOCK_OK, Gtk.ResponseType.OK)

        self.mainBox = self.get_content_area()
        # The "Add attachment" button.
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.mainBox.pack_start(box, False, False, 0)

        dbGtkUtils.add_button_to_container(box, "Add Defect",
                                           "Click to add a new defect.",
                                           self.add_defect)

        dbGtkUtils.add_button_to_container(box, "Remove Defect",
                                           "Click to remove selected defect.",
                                           self.remove_defect)

        # the list of attachments
        tree_view = self.create_tree_view()
        self.mainBox.pack_start(tree_view, True, True, 0)
        for C in self.defects:
            self.append_defect_to_view(C)

        self.show_all()

    def create_tree_view(self, size=150):
        """Create the tree view."""
        model = Gtk.ListStore(str, str)
        self.tree = Gtk.TreeView(model=model)
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.add(self.tree)
        scrolled.set_size_request(-1, size)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Defect Type", renderer, text=0)
        self.tree.append_column(column)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Description", renderer, text=1)
        self.tree.append_column(column)

        return scrolled

    def add_defect(self, *args):
        """A new defect."""
        values = dbGtkUtils.get_a_list_of_values("Insert new defect", ("Type", "Description/v"))
        if len(values):
            defect = {"name": values[0], "description": values[1]}
            self.defects.append(defect)
            self.append_defect_to_view(defect)

    def remove_defect(self, *args):
        """Remove a defect."""
        select = self.tree.get_selection()
        model, iter = select.get_selected()
        if iter:
            values = model[iter]
            for C in self.defects:
                if C["name"] == values[0] and C["description"] == values[1]:
                    rc = dbGtkUtils.ask_for_confirmation("Remove this Defect ?",
                                                         "{}\n{}\n".format(values[0], values[1]))
                    if rc:
                        self.defects.remove(C)
                        model.remove(iter)

                    break

    def append_defect_to_view(self, C):
        """Append a new defect to the triee view."""
        model = self.tree.get_model()
        model.append([C["name"], C["description"]])
