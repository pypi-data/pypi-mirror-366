#!/usr/bin/env python3
"""send shipments to a selected site.

Items can be added via a QR reader.
"""
import pathlib
import sys
import re

try:
    import itkdb_gtk

except ImportError:
    from pathlib import Path
    cwd = Path(__file__).parent.parent
    sys.path.append(cwd.as_posix())

from itkdb_gtk import dbGtkUtils, ITkDBlogin, ITkDButils, QRScanner

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio

# Check if Gtk can be open
gtk_runs, gtk_args = Gtk.init_check()


class CreateShipments(dbGtkUtils.ITkDBWindow):
    """Create a shipment from input."""

    def __init__(self, session, help_link=None):
        """Initialization.

        Args:
            session: ITkDB session.

        """
        self.model = None
        self.tree = None
        self.shipments = {}
        self.attachment = None
        global gtk_runs
        if gtk_runs:
            super().__init__(session=session, title="Create Shipment",
                             help_link=help_link, gtk_runs=gtk_runs)
            self.init_window()

    def init_window(self):
        """Initialize window."""
        # set border width
        self.set_border_width(10)

        # intercept keyboard
        self.scanner = QRScanner.QRScanner(self.get_qrcode)

        # Prepare HeaderBar
        self.hb.props.title = "Create Shipment"

        # action button in header
        button = Gtk.Button()
        icon = Gio.ThemedIcon(name="document-send-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        button.set_tooltip_text("Click to send shipment items.")
        button.connect("clicked", self.send_items)
        self.hb.pack_end(button)

        # Data panel
        grid = Gtk.Grid(column_spacing=5, row_spacing=1)
        self.mainBox.pack_start(grid, False, True, 0)

        # The recipient combo
        recipient = self.create_institute_combo()
        recipient.connect("changed", self.new_recipient)
        recipient.set_tooltip_text("Select the destination of the items.")
        lbl = Gtk.Label(label="Destination")
        lbl.set_xalign(0)
        grid.attach(lbl, 0, 0, 1, 1)
        grid.attach(recipient, 1, 0, 1, 1)

        # Shipment name
        self.name = Gtk.Entry()
        self.name.set_tooltip_text("Set the name of the shipment")
        lbl = Gtk.Label(label="Name")
        lbl.set_xalign(0)
        grid.attach(lbl, 0, 1, 1, 1)
        grid.attach(self.name, 1, 1, 1, 1)

        # Shipment comments.
        self.comments = Gtk.Entry()
        self.comments.set_tooltip_text("Type here your comments for hte shipment.")
        lbl = Gtk.Label(label="Comments")
        lbl.set_xalign(0)
        grid.attach(lbl, 0, 2, 1, 1)
        grid.attach(self.comments, 1, 2, 1, 1)

        # The "Add/Remove/Send Item" buttons.
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.mainBox.pack_start(box, False, False, 0)

        dbGtkUtils.add_button_to_container(box, "Add Items",
                                           "Click to add a new items.\nAdd SNs separated by\n\tnew line,\n\ttab\n\tespace or\n\tcomma.",
                                           self.add_item)

        dbGtkUtils.add_button_to_container(box, "Remove Item",
                                           "Click to remove selected Item.",
                                           self.remove_item)

        dbGtkUtils.add_button_to_container(box, "Send Items",
                                           "Click to send items.",
                                           self.send_items)

        dbGtkUtils.add_button_to_container(box, "Add Attch.",
                                           "Click to add an attachment.",
                                           self.add_attachment)

        dbGtkUtils.add_button_to_container(box, "Remove Attch.",
                                           "Click to remove the attachment.",
                                           self.remove_attachment)

        # Paned object
        paned = Gtk.Paned(orientation=Gtk.Orientation.VERTICAL)
        paned.set_size_request(-1, 200)
        self.mainBox.pack_start(paned, True, True, 0)

        # The list of items
        tree_view = self.create_tree_view()
        paned.add1(tree_view)

        # The text view
        paned.add2(self.message_panel.frame)

        self.show_all()

    def create_tree_view(self, size=150):
        """Creates tree view with the list of items."""
        model = self.get_tree_view_model()
        self.tree = Gtk.TreeView(model=model)
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.add(self.tree)
        scrolled.set_size_request(-1, size)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Serial No.", renderer, text=0)
        self.tree.append_column(column)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Nick", renderer, text=1)
        self.tree.append_column(column)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Object Type", renderer, text=2)
        self.tree.append_column(column)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Location", renderer, text=3)
        self.tree.append_column(column)

        return scrolled

    def new_recipient(self, combo):
        """A new recipient has been chosen."""
        name = self.get_institute_from_combo(combo)
        if name:
            self.recipient = name

    def new_destination(self, combo):
        """A new destination has been chosen."""
        name = self.get_institute_from_combo(combo)
        if name:
            self.destination = name

    def get_tree_view_model(self):
        """Return an empty model for the tree view."""
        return Gtk.ListStore(str, str, str, str, str)

    def add_item(self, *args):
        """Add new item."""
        # We will get the input either from a Dialog or from the QR reader.
        # For the later we get the SN in the argument list.
        if isinstance(args[0], Gtk.Button):
            txt = dbGtkUtils.get_a_value("Enter item SN", is_tv=True)
            if txt is None:
                return

            tmp = re.split(';|,| |\n|\t', txt)
            SNlist = [s.strip() for s in tmp if len(s.strip())>0]
        else:
            SNlist = [args[0]]

        for SN in SNlist:
            try:
                # Check that the object exists and get some information about it.
                rc = ITkDButils.get_DB_component(self.session, SN)
                if 'inTransit' in rc and rc['inTransit']:
                    dbGtkUtils.complain("Item {} is already in transit".format(SN),
                                        "This item is already in transit to {}".format(rc['shipmentDestination']['code']))
                    return

                nick = rc['alternativeIdentifier']
                obj_id = rc['id']
                obj = rc['componentType']['name']
                loc = rc['currentLocation']['code']
                serialN = rc['serialNumber']
                if serialN is None:
                    serialN = obj_id

                # Check tha tthe input is not already there
                model = self.tree.get_model()
                lv_iter = model.get_iter_first()
                while lv_iter:
                    if model.get_value(lv_iter, 0) == SN:
                        dbGtkUtils.complain("Duplicated item.",
                                            "Object {} is already in the list".format(SN))
                        return

                    lv_iter = model.iter_next(lv_iter)

                # Add the item in the liststore.
                model.append([serialN, nick, obj, loc, obj_id])

            except Exception:
                dbGtkUtils.complain("Error querying DB",
                                    "object {} does not exist.".format(SN))
                print(ITkDButils.get_db_response())

    def remove_item(self, *args):
        """Remove selected item."""
        select = self.tree.get_selection()
        model, lv_iter = select.get_selected()
        if lv_iter:
            values = model[lv_iter]
            rc = dbGtkUtils.ask_for_confirmation("Remove this items ?", values[0])
            if rc:
                model.remove(lv_iter)

    def add_attachment_dialog(self):
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

    def add_attachment(self, *args):
        """Add Attachment button clicked."""
        dlg = self.add_attachment_dialog()
        rc = dlg.run()
        if rc == Gtk.ResponseType.OK:
            try:
                path = pathlib.Path(dlg.fC.get_filename()).expanduser().resolve()
            except Exception as E:
                dbGtkUtils.complain("Could not create Attachment", str(E))
                dlg.hide()
                dlg.destroy()
                return

            T = dlg.att_title.get_text().strip()
            D = dlg.att_desc.get_text().strip()

            T = T if len(T) else None
            D = D if len(D) else None
            att = ITkDButils.Attachment(path=path, title=T, desc=D)
            self.attachment = att

        dlg.hide()
        dlg.destroy()

    def remove_attachment(self, *args):
        """Remove an existing attachment."""
        if self.attachment:
            self.attachment = None
            self.write_message("Attachment removed\n")
        else:
            self.write_message("No attachment found\n")

    def get_qrcode(self, txt):
        """Gets data from QR scanner."""
        self.write_message("{}\n".format(txt))

        # Try to add item to the list
        self.add_item(txt)

        return True

    def send_items(self, *args):
        """Send items in liststore."""
        model = self.tree.get_model()
        lv_iter = model.get_iter_first()
        items = []
        senders = {}
        while lv_iter:
            values = model[lv_iter]
            items.append(values[0])
            senders[values[3]] = senders.setdefault(values[3], 0) + 1
            lv_iter = model.iter_next(lv_iter)

        if len(items)>0:
            if len(senders) != 1:
                dbGtkUtils.complain("Too many senders.",
                                    "There are objects located in differen sites:{}".format('\n'.join(senders.keys())))
                return

            name = self.name.get_text()
            comments = self.comments.get_text()
            rc = ITkDButils.create_shipment(self.session,
                                            list(senders.keys())[0],
                                            self.recipient,
                                            items, name, True,
                                            comments=comments,
                                            attachment=self.attachment)
            if rc is None:
                rc = ITkDButils.get_db_response()
                ipos = rc.find("The following details may help:")
                msg = rc[ipos:]
                dbGtkUtils.complain("Error creting shipment.",
                                    "Could not send\n+ {}\n\n{}".format('\n+ '.join(items), msg))

            else:
                self.write_message("Successfully sent:\n+ {}\n".format('\n+ '.join(items)))
                model = self.get_tree_view_model()
                self.tree.set_model(model)
                self.comments.set_text("")
                self.name.set_text("")
                self.attachment = None

        else:
            self.write_message("Empty list of items when creating shipment.")


def main():
    """Main entry."""
    # main entry of the program
    HELP_LINK="https://itkdb-gtk.docs.cern.ch"

    dlg = ITkDBlogin.ITkDBlogin()
    client = dlg.get_client()
    if client is None:
        print("Could not connect to DB with provided credentials.")
        dlg.die()
        sys.exit()

    client.user_gui = dlg
    IS = CreateShipments(client, help_link="{}/createShipment.html".format(HELP_LINK))
    IS.set_accept_focus(True)
    IS.present()
    IS.connect("destroy", Gtk.main_quit)

    try:
        Gtk.main()

    except KeyboardInterrupt:
        print("Arrrgggg!!!")

    dlg.die()


if __name__ == "__main__":
    main()
