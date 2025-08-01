#!/usr/bin/env python3
"""Module Visual inspection GUI."""
import sys
import re
from pathlib import Path

try:
    import itkdb_gtk

except ImportError:
    cwd = Path(__file__).parent.parent
    sys.path.append(cwd.as_posix())

from itkdb_gtk import dbGtkUtils, ITkDBlogin, ITkDButils, QRScanner
from itkdb_gtk.ShowComments import ShowComments
from itkdb_gtk.ShowDefects import ShowDefects
from itkdb_gtk.ShowAttachments import ShowAttachments
from itkdb_gtk.UploadTest import UploadTest

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio


module_type = re.compile("20USE(M[0-5]{1}|[345]{1}[LR]{1})[0-9]{7}")
sensor_type = re.compile("20USES[0-5]{1}[0-9]{7}")


class ModuleVisualInspection(dbGtkUtils.ITkDBWindow):
    """Module/Sensor Visual Inspection."""

    def __init__(self, session, title="Visual Inspection", help_link=None):
        super().__init__(title=title,
                         session=session,
                         show_search="Find object with given SN.",
                         help_link=help_link)

        self.institute = self.pdb_user["institutions"][0]["code"]
        self.global_image = None
        self.global_link = None
        self.data = None
        self.currentStage = None
        self.attachments = []
        self.comments = []
        self.defects = []

        # action button in header
        button = Gtk.Button()
        icon = Gio.ThemedIcon(name="document-send-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        button.set_tooltip_text("Click to upload the test.")
        button.connect("clicked", self.upload_test)
        self.hb.pack_end(button)

        grid = Gtk.Grid(column_spacing=10, row_spacing=5)
        self.mainBox.pack_start(grid, False, False, 5)

        irow = 0
        receiver = self.create_institute_combo(only_user=True)
        receiver.connect("changed", self.on_institute)
        receiver.set_tooltip_text("Select the Institute making the test.")
        dbGtkUtils.set_combo_iter(receiver, self.institute)

        lbl = Gtk.Label(label="Institute")
        lbl.set_xalign(0)
        grid.attach(lbl, 0, irow, 1, 1)
        grid.attach(receiver, 1, irow, 1, 1)

        self.obj_type = None
        self.obj_type_label = Gtk.Label()
        self.obj_type_label.set_xalign(0)
        grid.attach(self.obj_type_label, 2, irow, 1, 1)

        irow += 1
        lbl = Gtk.Label(label="Serial Number")
        lbl.set_xalign(0)
        grid.attach(lbl, 0, irow, 1, 1)

        self.SN = dbGtkUtils.TextEntry(small=True)
        self.SN.connect("text_changed", self.SN_ready)
        self.SN.widget.set_tooltip_text("Enter SN of module.")
        grid.attach(self.SN.widget, 1, irow, 1, 1)


        self.passed = Gtk.Switch()
        self.passed.props.halign = Gtk.Align.START
        self.passed.set_active(True)
        lbl = Gtk.Label(label="Passed")
        lbl.set_xalign(0)
        grid.attach(lbl, 2, irow, 1, 1)
        grid.attach(self.passed, 3, irow, 1, 1)


        irow += 1
        lbl = Gtk.Label(label="Date")
        lbl.set_xalign(0)
        grid.attach(lbl, 0, irow, 1, 1)

        self.date = dbGtkUtils.TextEntry(small=True)
        grid.attach(self.date.widget, 1, irow, 1, 1)
        self.date.entry.set_text(ITkDButils.get_db_date())
        self.date.connect("text_changed", self.new_date)

        self.problems = Gtk.Switch()
        self.problems.props.halign = Gtk.Align.START
        self.problems.set_active(False)
        lbl = Gtk.Label(label="Problems")
        lbl.set_xalign(0)
        grid.attach(lbl, 2, irow, 1, 1)
        grid.attach(self.problems, 3, irow, 1, 1)

        irow +=1
        self.reception = Gtk.Switch()
        self.reception.props.halign = Gtk.Align.START
        self.reception.set_active(False)
        lbl = Gtk.Label(label="Reception VI")
        lbl.set_xalign(0)
        grid.attach(lbl, 0, irow, 1, 1)
        grid.attach(self.reception, 1, irow, 1, 1)

        irow +=1
        lbl = Gtk.Label()
        grid.attach(lbl, 0, irow, 1, 1)

        # The "Add attachment" button.
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.mainBox.pack_start(box, False, False, 0)
        self.btn_attch = dbGtkUtils.add_button_to_container(box, "Attachments",
                                           "Click to edit attachments.",
                                           self.edit_attachments)

        self.btn_comments = dbGtkUtils.add_button_to_container(box, "Comments",
                                           "Click to edit comments.",
                                           self.edit_comments)

        self.btn_defects = dbGtkUtils.add_button_to_container(box, "Defects",
                                           "Click to edit defects.",
                                           self.edit_defects)

        self.mainBox.pack_start(self.message_panel.frame, True, True, 5)
        self.write_message("Module Visual Inspection\n")
        self.show_all()

        self.scanner = QRScanner.QRScanner(self.get_qrcode)

    def on_institute(self, combo):
        """A new recipient has been chosen."""
        name = self.get_institute_from_combo(combo)
        if name:
            self.institute = name

    def new_date(self, entry, value):
        """new date given at input."""
        d = dbGtkUtils.parse_date_as_string(value)
        if d is not None:
            self.date.set_text(d)

    def SN_ready(self, *args):
        """SN is ready in the TextEnttry."""
        SN = self.SN.get_text()
        # GEt children.
        module = ITkDButils.get_DB_component(self.session, SN)
        if module is None:
            self.write_message(ITkDButils.get_db_response())
            return

        SN = module["serialNumber"]
        if module_type.match(SN):
            self.obj_type_label.set_markup("<b><big>Module</big></b>")
            self.obj_type = "MODULE"
        elif sensor_type.match(SN):
            self.obj_type_label.set_markup("<b><big>Sensor</big></b>")
            self.obj_type = "SENSOR"
        else:
            self.obj_type_label.set_text("Invalid SN")
            self.obj_type = None
            dbGtkUtils.complain("Invalid SN", "Not a module nor a sensor.")

        self.reception.set_sensitive(True)
        self.reception.set_active(False)
        self.currentStage = module["currentStage"]["code"]
        if self.obj_type == "MODULE" and self.currentStage in ["AT_LOADING_SITE", "STITCH_BONDING"]:
            self.reception.set_active(True)
            self.reception.set_sensitive(False)

        args[0].set_text(SN)


    def edit_attachments(self, *args):
        """Edit test attachmetns."""
        SA = ShowAttachments("Test Attachments", self.session, self.attachments, parent=self)
        response = SA.run()
        if response == Gtk.ResponseType.OK:
            self.attachments = SA.attachments

        SA.hide()
        SA.destroy()

        if len(self.attachments) > 0:
            self.btn_attch.set_label("Attachments ({})".format(len(self.attachments)))

    def edit_comments(self, *args):
        """Edit test comments."""
        SC = ShowComments("Test Comments", self.comments, self)
        rc = SC.run()
        if rc == Gtk.ResponseType.OK:
            self.comments = SC.comments

        SC.hide()
        SC.destroy()

        if len(self.comments) > 0:
            self.btn_comments.set_label("Comments ({})".format(len(self.comments)))

    def edit_defects(self, *args):
        """Edit test defects."""
        SD = ShowDefects("Test Defects", self.defects, self)
        rc = SD.run()
        if rc == Gtk.ResponseType.OK:
            self.defects = SD.defects

        SD.hide()
        SD.destroy()

        if len(self.defects) > 0:
            self.btn_defects.set_label("Defects ({})".format(len(self.defects)))

    def upload_test(self, *args):
        """Upload the test."""
        SN = self.SN.get_text()
        if len(SN) == 0 or self.obj_type is None:
            dbGtkUtils.complain("Invalid Serial Number", SN)
            return

        defaults = {
            "component": SN,
            "institution": self.institute,
            "passed": self.passed.get_active(),
            "problems": self.problems.get_active(),
            "runNumber": "1",
            "date": self.date.get_text()
        }

        test_type = "VISUAL_INSPECTION"
        if self.obj_type == "SENSOR":
            test_type = "VIS_INSP_RES_MOD_V2"

        else:
            if self.reception.get_active():
                test_type = "VISUAL_INSPECTION"

        self.data = ITkDButils.get_test_skeleton(self.session,
                                                 self.obj_type,
                                                 test_type,
                                                 defaults)

        self.data["comments"] = self.comments
        self.data["defects"] = self.defects
        uploadW = UploadTest(self.session, self.data, self.attachments)



    def get_qrcode(self, txt):
        """Read SN from scanner."""
        self.write_message("SN: {}\n".format(txt))
        self.SN_ready(txt, self.SN.widget)


def main():
    """Main entry."""
    HELP_LINK="https://itkdb-gtk.docs.cern.ch/moduleVisualInspection.html"

    # DB login
    dlg = ITkDBlogin.ITkDBlogin()
    client = dlg.get_client()
    if client is None:
        print("Could not connect to DB with provided credentials.")
        dlg.die()
        sys.exit()

    client.user_gui = dlg

    gTest = ModuleVisualInspection(client, help_link=HELP_LINK)

    gTest.present()
    gTest.connect("destroy", Gtk.main_quit)
    try:
        Gtk.main()

    except KeyboardInterrupt:
        print("Arrrgggg!!!")

    dlg.die()

if __name__ == "__main__":
    main()
