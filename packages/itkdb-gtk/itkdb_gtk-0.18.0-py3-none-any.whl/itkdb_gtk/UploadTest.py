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

from itkdb_gtk import dbGtkUtils, ITkDBlogin, ITkDButils
from itkdb_gtk.ShowComments import ShowComments
from itkdb_gtk.ShowAttachments import ShowAttachments
from itkdb_gtk.ShowDefects import ShowDefects

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio

# Check if Gtk can be open
gtk_runs, gtk_args = Gtk.init_check()


def create_json_data_editor(data):
    """Create a dialog to show the JSon file."""
    dlg = Gtk.Dialog(title="Test Data")
    dlg.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                    Gtk.STOCK_OK, Gtk.ResponseType.OK)

    dlg.set_property("height-request", 500)
    box = dlg.get_content_area()
    value = dbGtkUtils.DictDialog(data)
    scrolled = Gtk.ScrolledWindow()
    scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
    scrolled.add(value)
    box.pack_start(scrolled, True, True, 10)

    dlg.show_all()
    return value, dlg


def check_data(data):
    """Checks validity of JSon data.

    Args:
        data (): The json data

    Returns:
        boolean: True if valid, False otherwise.

    """
    errors = []
    missing = []
    if "component" not in data:
        errors.append("Need reference to component, hex string")
        missing.append("component")

    if "testType" not in data:
        errors.append("Need to know test type, short code")
        missing.append("testType")

    if "institution" not in data:
        errors.append("Need to know institution, short code")
        missing.append("institution")

    if "results" not in data:
        errors.append("Need some test results")
        missing.append("results")

    return errors, missing


class UploadTest(dbGtkUtils.ITkDBWindow):
    """Collects information to upload a test and its attachments."""

    def __init__(self, session, payload=None, attachment=None, help_link=None):
        """Initialization.

        Args:
            session: ITkDB session
            payload: path of test file
            attachment: an Attachment object or list of attachments.

        """
        self.payload = payload
        self.data = None
        self.folder = None
        self.attachments = []
        self.comments = []
        self.defects = []
        self.currentStage = None
        if attachment is not None:
            if isinstance(attachment, ITkDButils.Attachment):
                if attachment.path is not None:
                    self.attachments.append(attachment)
            else:
                try:
                    for att in attachment:
                        self.attachments.append(att)

                except TypeError:
                    print("Wrong attachment: {}".format(attachment))

        global gtk_runs
        if gtk_runs:
            super().__init__(session=session, title="Upload Test", gtk_runs=gtk_runs, help_link=help_link)
            self.init_window()

    def init_window(self):
        """Creates the Gtk window."""
        # Initial tweaks
        self.set_border_width(10)

        # Prepare HeaderBar
        self.hb.props.title = "Upload Tests"

        # Active button in header
        button = Gtk.Button()
        icon = Gio.ThemedIcon(name="document-send-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        button.set_tooltip_text("Click to upload test")
        button.connect("clicked", self.upload_test_gui)
        self.hb.pack_end(button)

        # Data panel
        grid = Gtk.Grid(column_spacing=5, row_spacing=1)
        self.mainBox.pack_start(grid, True, False, 0)

        # The test file widgets
        lbl = Gtk.Label(label="Test file")
        lbl.set_xalign(0)
        grid.attach(lbl, 0, 0, 1, 1)

        self.testF = Gtk.FileChooserButton()
        self.testF.set_tooltip_text("Click to select JSon test file.")

        grid.attach(self.testF, 1, 0, 1, 1)
        self.testF.connect("file-set", self.on_test_file)

        # This is to show/edit the test file data
        btn = Gtk.Button()
        icon = Gio.ThemedIcon(name="view-paged-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        btn.add(image)
        btn.set_tooltip_text("Click to view/edit test data.")
        btn.connect("clicked", self.show_data)
        grid.attach(btn, 2, 0, 1, 1)

        # Object Data
        lbl = Gtk.Label(label="Serial Number")
        lbl.set_xalign(0)
        grid.attach(lbl, 0, 1, 1, 1)

        self.entrySN = Gtk.Entry()
        grid.attach(self.entrySN, 1, 1, 1, 1)

        # Test type
        lbl = Gtk.Label(label="Test Type")
        lbl.set_xalign(0)
        grid.attach(lbl, 0, 2, 1, 1)

        self.entryTest = Gtk.Entry()
        grid.attach(self.entryTest, 1, 2, 1, 1)

        # Object Stage
        lbl = Gtk.Label(label="Object Stage")
        lbl.set_xalign(0)
        grid.attach(lbl, 0, 3, 1, 1)

        self.objStage = Gtk.ComboBoxText.new()
        self.objStage.connect("changed", self.on_new_stage)
        grid.attach(self.objStage, 1, 3, 1, 1)

        self.isRetroactive = Gtk.ToggleButton.new_with_label("RetroActive")
        grid.attach(self.isRetroactive, 2, 3, 1, 1)


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

        dbGtkUtils.add_button_to_container(box, "Upload Test",
                                           "Click to upload test.",
                                           self.upload_test_gui)

        # The text view
        self.mainBox.pack_start(self.message_panel.frame, True, True, 0)

        self.show_all()

        if self.payload:
            try:
                the_path = Path(self.payload).expanduser().resolve()
                if the_path.exists():
                    ifile = Path(self.payload).expanduser().resolve().as_posix()
                    self.testF.set_filename(ifile)
                    self.on_test_file(self.testF)
                    self.write_message("Loaded {}\n".format(the_path.name))

                else:
                    print("Input file does not exists: {}".format(self.payload))

            except TypeError:
                self.load_payload(self.payload)
                self.write_message("Loaded memory payload.\n")
                self.testF.set_sensitive(False)

        if len(self.attachments) > 0:
            self.btn_attch.set_label("Attachments ({})".format(len(self.attachments)))

        if len(self.comments) > 0:
            self.btn_comments.set_label("Comments ({})".format(len(self.comments)))

        if len(self.defects) > 0:
            self.btn_defects.set_label("Defects ({})".format(len(self.defects)))


    def get_test_institute(self):
        """Select an institue."""
        dlg = Gtk.Dialog(title="Select Institution.", flags=0)
        dlg.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                        Gtk.STOCK_OK, Gtk.ResponseType.OK)
        area = dlg.get_content_area()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        area.add(box)

        box.pack_start(Gtk.Label(label="Select an Institute"), False, True, 0)

        combo = self.create_institute_combo()
        box.pack_start(combo, False, True, 5)

        dlg.show_all()
        rc = dlg.run()

        out = None
        if rc == Gtk.ResponseType.OK:
            out = self.get_institute_from_combo(combo)

        dlg.hide()
        dlg.destroy()
        return out

    def load_payload(self, data):
        """Payload is given as a dict."""
        self.data = data
        errors, missing = check_data(self.data)
        self.complete_missing(missing, errors)
        self.set_stages()

    def on_new_stage(self, *args):
        """New stage selected."""
        stg = self.objStage.get_active_text()
        changed = (stg != self.currentStage)
        self.isRetroactive.set_active(changed)
        self.data["isRetroactive"] = changed
        if changed:
            self.data["stage"] = stg
        else:
            if "stage" in self.data:
                del self.data["stage"]

    def set_stages(self):
        """Prepare the stages combo."""
        # Check the object stage
        SN = self.data["component"]
        try:
            obj = ITkDButils.get_DB_component(self.session, SN)
            self.currentStage = obj["currentStage"]["code"]

            self.objStage.remove_all()
            indx = 0
            for i, stg in enumerate(obj["stages"]):
                S = stg["code"]
                self.objStage.append_text(S)
                if S == self.currentStage:
                    indx = i

            self.objStage.set_active(indx)

        except Exception:
            self.write_message("Something went wrong with the stages\n")


    def on_test_file(self, fdlg):
        """Test file browser clicked."""
        fnam = fdlg.get_filename()
        self.folder = Path(fnam).parent

        # The file exists by definition
        try:
            self.data = json.loads(open(fnam, encoding="UTF-8").read())
            errors, missing = check_data(self.data)
            self.complete_missing(missing, errors)
            self.set_stages()

        except Exception as E:
            self.data = None
            self.write_message("Cannot load file {}\n".format(fnam))
            self.write_message("{}\n".format(str(E)))

    def complete_missing(self, missing, errors):
        """Completes missing parts."""
        if len(missing):
            self.write_message("Some keys are missing in the JSon file.\n")
            self.write_message("{}\n".format("\n".join(['\t'+line for line in missing])))

            if "institution" in missing and len(missing) == 1:
                site = self.get_test_institute()
                if site:
                    self.data["institution"] = site
                    self.write_message("Setting Institution to {}\n".format(self.data["institution"]))

            else:
                dbGtkUtils.complain("Invalid JSON data\n{}".format('\n'.join(errors)))

        self.find_attachments()
        self.find_comments()
        self.find_defects()

        self.entrySN.set_text(self.data["component"] if self.data["component"] else "")
        self.entryTest.set_text(self.data["testType"])
        self.comments = self.data.get("comments", [])
        self.defects = self.data.get("defects", [])


    def show_data(self, *args):
        """Show data button clicked."""
        if self.data is None:
            return

        value, dlg = create_json_data_editor(self.data)
        rc = dlg.run()
        if rc == Gtk.ResponseType.OK:
            self.data = value.values

        dlg.hide()
        dlg.destroy()

    def find_attachments(self):
        """Find Attachments in payload."""
        # We used to clean the attachmetns, but this would remove the ones given
        # in the contructor.
        # self.attachments = []
        if "attachments" in self.data:
            for A in self.data["attachments"]:
                if not Path(A["path"]).exists():
                    if self.folder:
                        the_path = self.folder.joinpath(A["path"])
                    else:
                        continue
                else:
                    the_path = Path(A["path"]).expanduser().resolve()

                self.attachments.append(ITkDButils.Attachment(path=the_path, title=A["title"], desc=A["description"]))

        if len(self.attachments) > 0:
            self.btn_attch.set_label("Attachments ({})".format(len(self.attachments)))

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

    def find_comments(self):
        """Find comments in payload"""
        self.comments = []
        if "comments" in self.data:
            for C in self.data["comments"]:
                self.comments.append(C)

        if len(self.comments) > 0:
            self.btn_comments.set_label("Comments ({})".format(len(self.comments)))

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


    def find_defects(self):
        """Find defects in payload."""
        self.defects = []
        if "defects" in self.data:
            for D in self.data["defects"]:
                self.defects.append(D)

        if len(self.defects) > 0:
            self.btn_defects.set_label("Defects ({})".format(len(self.defects)))

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

    def upload_test_gui(self, *args):
        """Uploads test and attachments."""
        self.upload_test()

    def upload_test(self):
        """Uploads test and attachments."""
        if self.data is None:
            self.write_message("No data available to upload\n")
            return

        self.data["comments"] = self.comments
        self.data["defects"] = self.defects

        rc = ITkDButils.upload_test(self.session, self.data, self.attachments, check_runNumber=True)
        if rc:
            ipos = rc.find("The following details may help:")
            msg = rc[ipos:]
            dbGtkUtils.complain("Failed uploading test", msg)

        else:
            self.write_message("Upload successfull\n")
            dbGtkUtils.ask_for_confirmation("Upload successfull", "")


def main():
    """Main entry."""
    HELP_LINK="https://itkdb-gtk.docs.cern.ch/uploadSingleTest.html"
    parser = argparse.ArgumentParser()

    parser.add_argument("--test-file", help="Name of json file with test data")
    parser.add_argument("--component-id", help="Override component code")
    parser.add_argument("--raw_data", help="Raw data file", default=None)
    parser.add_argument("--attachment", help="Attachment to upload with the test", default=None)
    parser.add_argument("--attach_title", default=None, type=str, help="The attachment description")
    parser.add_argument("--attach_desc", default="", type=str, help="The attachment description")
    parser.add_argument("--verbose", action="store_true", help="Print what's being sent and received")

    args = parser.parse_args()

    # DB login
    dlg = ITkDBlogin.ITkDBlogin()
    client = dlg.get_client()
    if client is None:
        print("Could not connect to DB with provided credentials.")
        dlg.die()
        sys.exit()

    client.user_gui = dlg

    # Start GUI
    UpT = UploadTest(client,
                     payload=args.test_file,
                     help_link=HELP_LINK,
                     attachment=ITkDButils.Attachment(path=args.attachment,
                                                      title=args.attach_title,
                                                      desc=args.attach_desc))

    if gtk_runs:
        UpT.present()
        UpT.connect("destroy", Gtk.main_quit)
        try:
            Gtk.main()

        except KeyboardInterrupt:
            print("Arrrgggg!!!")

    else:
        # Think
        pass

    dlg.die()


if __name__ == "__main__":
    main()
