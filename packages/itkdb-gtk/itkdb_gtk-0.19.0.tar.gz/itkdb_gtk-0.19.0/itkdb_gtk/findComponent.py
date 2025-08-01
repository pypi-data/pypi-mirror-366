#!/usr/bin/env python3
"""GUI to upload tests."""
import argparse
import json
import sys
from pathlib import Path

try:
    import itkdb_gtk

except ImportError:
    cwd = Path(__file__).parent.parent
    sys.path.append(cwd.as_posix())

from itkdb_gtk import dbGtkUtils, ITkDBlogin, ITkDButils, QRScanner
from itkdb_gtk.GetShipments import find_vtrx


import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio

class FindComponent(dbGtkUtils.ITkDBWindow):
    """Read QR of bar code and retrieve information about component."""

    def __init__(self, session, help_link=None):
        """Initialization.

        Args:
            session: ITkDB session
            help_link: link to help page.

        """
        super().__init__(session=session, title="Find Component", help_link=help_link)
        self.scanner = QRScanner.QRScanner(self.get_qrcode)
        self.init_window()

    def init_window(self):
        """Create the Gtk window."""
        # Initial tweaks
        self.set_border_width(10)

        # Prepare HeaderBar
        self.hb.props.title = "Find Component"

        # Object Data
        lbl = Gtk.Label(label="Scan your QR or bar code. Information will appear below.")
        self.mainBox.pack_start(lbl, False, False, 10)

        #btn = Gtk.Button(label="Test Button")
        #btn.connect("clicked", self.test_qrcode)
        #self.mainBox.pack_start(btn, True, True, 0)

        # The text view
        self.mainBox.pack_start(self.message_panel.frame, True, True, 0)

        self.show_all()

    def get_qrcode(self, txt):
        """Gets data from QR scanner."""
        if txt.find("J-SD") == 0:
            try:
                SN = find_vtrx(self.session, txt)
            except ValueError as e:
                self.write_message("Error: {}\n".format(e))
                return
        else:
            SN = txt

        obj = ITkDButils.get_DB_component(self.session, SN)
        if obj is None:
            self.write_message("Object not found in DB\n")
            return

        msg = "\n{}\nObject SN: {}\nObject Alt. ID: {}\nObject Type: {}\nObject Loc. {}\nObject stage: {} - {}\n".format(
            txt,
            obj["serialNumber"],
            obj["alternativeIdentifier"],
            obj["componentType"]["name"],
            obj["currentLocation"]["name"],
            obj["currentStage"]["code"],
            obj["currentStage"]["name"])

        self.write_message(msg)

    def test_qrcode(self, *args):
        """Gets data from QR scanner."""
        txt = "a3c671bf38d3957dc053c6e5471aa27e"
        self.write_message("{}\n".format(txt))

        if txt.find("J-SD") == 0:
            try:
                SN = find_vtrx(self.session, txt)
            except ValueError as e:
                self.write_message("Error: {}\n".format(e))
                return
        else:
            SN = txt

        obj = ITkDButils.get_DB_component(self.session, SN)
        if obj is None:
            self.write_message("Object not found in DB\n")
            return


        msg = "\n\nObject SN: {}\nObject Alt. ID: {}\nObject Type: {}\nObject Loc.: {}\nObject stage: {} - {}\n".format(
            obj["serialNumber"],
            obj["alternativeIdentifier"],
            obj["componentType"]["name"],
            obj["currentLocation"]["name"],
            obj["currentStage"]["code"],
            obj["currentStage"]["name"])

        self.write_message(msg)
        self.write_message("")

def main():
    """Main entry."""
    HELP_LINK="https://itkdb-gtk.docs.cern.ch/uploadSingleTest.html"

    # DB login
    dlg = ITkDBlogin.ITkDBlogin()
    client = dlg.get_client()
    if client is None:
        print("Could not connect to DB with provided credentials.")
        dlg.die()
        sys.exit()

    client.user_gui = dlg

    window = FindComponent(client, help_link=HELP_LINK)
    window.set_accept_focus(True)
    window.present()
    window.connect("destroy", Gtk.main_quit)

    try:
        Gtk.main()

    except KeyboardInterrupt:
        print("Arrrgggg!!!")

    dlg.die()

if __name__ == "__main__":
    main()