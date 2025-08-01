#!/usr/bin/env python3
"""Shows comments."""

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


class ShowComments(Gtk.Dialog):
    """Edit comments"""
    def __init__(self, title, comments=[], parent=None):
        """Initialization."""
        super().__init__(title=title, transient_for=parent)
        self.comments = [C for C in comments]
        self.init_window()

    def init_window(self):
        """Preapare the window."""
        self.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                         Gtk.STOCK_OK, Gtk.ResponseType.OK)

        self.mainBox = self.get_content_area()
        # The "Add attachment" button.
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.mainBox.pack_start(box, False, False, 0)

        dbGtkUtils.add_button_to_container(box, "Add Comment",
                                           "Click to add a new comment.",
                                           self.add_comment)

        dbGtkUtils.add_button_to_container(box, "Remove Comment",
                                           "Click to remove selected comment.",
                                           self.remove_comment)

        # the list of attachments
        tree_view = self.create_tree_view()
        self.mainBox.pack_start(tree_view, True, True, 0)
        for C in self.comments:
            self.append_comment_to_view(C)

        self.show_all()

    def create_tree_view(self, size=150):
        """Create the tree view."""
        model = Gtk.ListStore(str)
        self.tree = Gtk.TreeView(model=model)
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.add(self.tree)
        scrolled.set_size_request(-1, size)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Comment", renderer, text=0)
        self.tree.append_column(column)

        return scrolled

    def add_comment(self, *args):
        """A new comment."""
        text = dbGtkUtils.get_a_value("Comment", "Add a new comment", True, self)
        self.comments.append(text)
        self.append_comment_to_view(text)

    def remove_comment(self, *args):
        """Remove a comment."""
        select = self.tree.get_selection()
        model, iter = select.get_selected()
        if iter:
            values = model[iter]
            for C in self.comments:
                if C == values[0]:
                    rc = dbGtkUtils.ask_for_confirmation("Remove this Comment ?",
                                                         "{}".format(values[0]))
                    if rc:
                        self.comments.remove(C)
                        model.remove(iter)

                    break

    def append_comment_to_view(self, C):
        """Append a new comment to the triee view."""
        model = self.tree.get_model()
        model.append([C])
