#!/usr/bin/env python3
"""Creates Module Glue Weight Json from input file and upload."""
import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path

try:
    import itkdb_gtk

except ImportError:
    cwd = Path(__file__).parent.parent
    sys.path.append(cwd.as_posix())

from itkdb_gtk import dbGtkUtils, ITkDBlogin, ITkDButils, UploadMultipleTests
HELP_LINK="https://itkdb-gtk.docs.cern.ch"


import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio

# Check if Gtk can be open
gtk_runs, gtk_args = Gtk.init_check()


def str2bool(v):
    """Boolean from string."""
    return v.lower() in ("yes", "true", "t", "1")


def find_module(ifile, module_sn="MODULE_SN"):
    """Find the starting line of a module.

    Args:
        ifile: the input file object.
        module_sn: tag t ostar t a new module.

    Returns:
        the SN of the module.

    """
    line = ifile.readline()
    if line is None:
        return None

    while line:
        if module_sn in line:
            data = [x.strip() for x in line.split()]
            if len(data) != 2:
                print("Inconsisten data line should be: MODULE_SN serial_number")

            if len(data) >= 2:
                return data[1]
            else:
                line = ifile.readline()

        else:
            line = ifile.readline()

    return None


def remove_defaul_keys(data, default_value=-9999):
    """Remove keys with deafault value.

    Args:
        data: Input dictionary
        default_value: Defaultvalue. Defaults to -9999.

    Returns:
        data: trimmed dictionary

    """
    keys = []
    for key, val in data.items():
        if val == default_value:
            keys.append(key)

    for key in keys:
        del data[key]

    return data


class GlueWeight(dbGtkUtils.ITkDBWindow):
    """Upluead Glue Weight test."""

    def __init__(self, session, ifile=None, help_link=None):
        """Initialization.

        Args:
            session: ITkDB session_
            ifile (optional): Input file. Defaults to None.

        """
        self.ifile = ifile
        self.session = session
        self.modules = []
        self.test_list = []
        self.test_index = {}

        defaults = {
            "institution": "IFIC",
            "runNumber": "1",
            "properties": {
                "START_DATE": ITkDButils.get_db_date(),
                "FINISH_DATE": ITkDButils.get_db_date()
            }
        }
        self.skeleton = ITkDButils.get_test_skeleton(
            session, "MODULE", "GLUE_WEIGHT", defaults)

        global gtk_runs
        if gtk_runs:
            super().__init__(session=session,
                             title="Upload Glue Weight",
                             help_link=help_link)
            self.init_window()
        else:
            self.pdb_user = ITkDButils.get_db_user(session)

    def init_window(self):
        """Initialize window."""
        #
        # Prepare HeaderBar
        self.set_border_width(10)

        # Prepare HeaderBar
        self.hb.props.title = "Glue height"

        # file entry and search button
        self.file_name = Gtk.FileChooserButton()
        self.file_name.connect("file-set", self.on_file_set)
        self.mainBox.pack_start(self.file_name, False, True, 0)
        if self.ifile and self.ifile.name:
            self.file_name.set_filename(self.ifile.name)

        # Add a Separator
        self.mainBox.pack_start(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL), False, True, 0)

        # The notebook
        self.notebook = Gtk.Notebook()
        self.notebook.set_tab_pos(Gtk.PositionType.LEFT)
        self.mainBox.pack_start(self.notebook, True, True, 20)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.set_border_width(5)

        label = Gtk.Label()
        label.set_markup("<big>You should select a file using the file selector above</big>")
        label.set_line_wrap(True)
        box.pack_end(label, True, True, 0)
        self.notebook.append_page(box)

        if self.ifile:
            self.modules = self.parse_file(self.ifile)
            self.populate_notebook()



        # The text view
        self.mainBox.pack_end(self.message_panel.frame, True, True, 5)

        # The button box
        btnBox = Gtk.ButtonBox(orientation=Gtk.Orientation.HORIZONTAL)
        self.buttons = []

        btn = Gtk.Button(label="Reload file")
        btn.connect("clicked", self.on_read_file)
        btnBox.add(btn)

        btn = Gtk.Button(label="Upload Tests")
        btn.connect("clicked", self.on_upload)
        if self.ifile is None or self.ifile.name is None:
            btn.set_sensitive(False)

        self.buttons.append(btn)
        btnBox.add(btn)

        self.mainBox.pack_start(btnBox, False, True, 0)

        self.show_all()

    def create_test_window(self, test_json, test_name, label):
        """Create the dialog for a DB test and add it to the notebook.

        Args:
            test_json: The JSon-like dict with the values
            test_name: The name of the test for internal indexing
            label: The label for the Notebook

        Returns:
            The box containing the data.

        """
        scrolled, gM = dbGtkUtils.create_scrolled_dictdialog(test_json)
        self.test_list.append(gM)
        self.test_index[test_name] = len(self.test_list) - 1
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.set_border_width(5)
        box.pack_end(scrolled, True, True, 0)
        box.dict_dialog = gM
        gM.box = box
        self.notebook.append_page(box, Gtk.Label(label=label))

        return box

    def populate_notebook(self):
        """Populate noebook."""
        dbGtkUtils.empty_container(self.notebook)
        self.test_list = []
        self.test_index = {}

        for m in self.modules:
            self.create_test_window(m, m["component"], m["component"])

        self.notebook.show_all()

    def on_file_set(self, *args):
        """Call when file chosen in FileChooser."""
        self.on_read_file(None)

    def on_upload(self, *args):
        """Upload tests to DB."""
        self.upload_tests()

    def on_read_file(self, widget):
        """Read file button clicked."""
        path = self.file_name.get_filename()
        if path is None or not Path(path).exists():
            dbGtkUtils.complain("Could not find Production File", path, parent=self)
            return

        self.read_file(path)
        self.populate_notebook()
        for btn in self.buttons:
            btn.set_sensitive(True)

    def upload_current_test(self, *args):
        """Upload test i ncurrent window."""
        pass

    def read_file(self, path):
        """Parse file."""
        with open(path, "r", encoding="UTF-8") as ifile:
            self.modules = self.parse_file(ifile)

    def parse_file(self, ifile, module_sep="MODULE_SN"):
        """Parse a data file.

        Args:
            ifile (): A file object.
            module_sep: tag to idenntify a new module.

        Returns:
            a list of tests (json)

        """
        ifile.seek(0, 0)

        # Now get the modules in the file
        modules = []
        while True:
            SN = find_module(ifile, module_sn=module_sep)
            if SN is None:
                break

            modules.append((SN, ifile.tell()))

        # Read the module data block
        module_data = []
        for SN, ipos in modules:
            ifile.seek(ipos, 0)

            line = ifile.readline()
            test_json = deepcopy(self.skeleton)
            test_json["component"] = SN
            while line:
                if module_sep in line:
                    break

                if line[0] == '#':
                    line = ifile.readline()
                    continue

                data = [x.strip() for x in line.split()]
                if len(data) < 2:
                    line = ifile.readline()
                    continue

                if data[0] in test_json["properties"]:
                    if isinstance(test_json["properties"][data[0]], str):
                        test_json["properties"][data[0]] = data[1]
                    else:
                        test_json["properties"][data[0]] = float(data[1])

                elif data[0] in test_json["results"]:
                    test_json["results"][data[0]] = float(data[1])

                else:
                    key = data[0].lower()
                    if key == "comments":
                        txt = " ".join(data[1:]).split(';')
                        comments = [x.strip() for x in txt]
                        test_json["comments"] = comments

                    if key == "defects":
                        txt = " ".join(data[1:]).split(':')
                        defect = [x.strip() for x in txt]
                        test_json["defects"].append({
                            "name": defect[0],
                            "description": defect[1],
                            "properties": {}
                        })

                    else:
                        if key == "passed":
                            test_json["passed"] = str2bool(data[1])

                        elif key == "problems":
                            test_json["problems"] = str2bool(data[1])

                line = ifile.readline()

            # clean up
            # remove_defaul_keys(test_json["properties"])
            remove_defaul_keys(test_json["results"])
            module_data.append(test_json)

        return module_data

    def upload_tests(self):
        """Upload tests to DB."""
        W = UploadMultipleTests.UploadMultipleTests(
            self.session,
            help_link="{}/uploadMultipleTests.html".format(HELP_LINK)
        )
        
        if len(self.test_list)>0:
            for G in self.test_list:
                m = G.values
                W.add_test_data_to_view(m)
                

        else:
            for m in self.modules:
                W.add_test_data_to_view(m)


def main():
    """Main entry."""
    # Get input file
    parser = argparse.ArgumentParser(description="GlueTest")
    parser.add_argument('files', nargs='*', help="Input files")
    parser.add_argument("--separator", default="MODULE_SN", help="Key for module serial number.")
    options = parser.parse_args()

    if not gtk_runs:
        if len(options.files) == 0:
            print("I need an input file")
            sys.exit(1)

        try:
            ifile = open(options.files[0], 'r')

        except Exception as e:
            print(e)
            sys.exit()

    else:
        try:
            ifile = open(options.files[0], 'r') if len(options.files)>0 else None

        except Exception as e:
            print(e)
            ifile = None

    # Connect to DB and get the test skeleton
    dlg = ITkDBlogin.ITkDBlogin()
    session = dlg.get_client()
    if session is None:
        print("Could not connect to DB with provided credentials.")
        sys.exit()

    GW = GlueWeight(session, ifile, help_link=HELP_LINK)
    if gtk_runs:
        GW.show_all()
        GW.set_accept_focus(True)
        GW.present()
        GW.connect("destroy", Gtk.main_quit)

        try:
            Gtk.main()

        except KeyboardInterrupt:
            print("Arrrgggg!!!")

    else:
        GW.modules = GW.parse_file(ifile)
        print(json.dumps(GW.modules, indent=2))
        GW.upload_tests()
        ifile.close()

    dlg.die()


if __name__ == "__main__":
    main()
