#!/usr/bin/env python3
"""Read IV files and create plots.

Analisis de la IV con macros de la webApp

SENSOR_IV_Analysis.py in
https://gitlab.cern.ch/atlas-itk/sw/db/production_database_scripts.git

webApp aqui:
https://itk-pdb-webapps-strips.web.cern.ch

"""
import sys
import os
import json
import tempfile
import copy
from pathlib import Path

from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
from matplotlib.backends.backend_gtk3 import NavigationToolbar2GTK3 as NavigationToolbar
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio

try:
    import itkdb_gtk

except ImportError:
    cwd = Path(__file__).parent.parent
    sys.path.append(cwd.as_posix())

from itkdb_gtk import dbGtkUtils, ITkDBlogin, ITkDButils, UploadTest, SensorUtils

# Check if Gtk can be open
gtk_runs, gtk_args = Gtk.init_check()


def remove_files(W, flist):
    """Remove files given in the input list.

    Args:
        flist (list): list of filenames.

    """
    for f in flist:
        os.unlink(f)


class IVwindow(dbGtkUtils.ITkDBWindow):
    """GUI for IV file handling."""

    def __init__(self, session, title="IV window", options=None, help_link=None):
        """Initialization."""
        super().__init__(session=session, title=title,
                         show_search=None, gtk_runs=gtk_runs,
                         help_link=help_link
                         )
        self.mdata = {}
        self.mod_type = {}
        self.mod_SN = {}
        self.last_folder = None
        self.difference = None
        self.canvas = None

        self.init_window()

    def init_window(self):
        """Prepare the Gtk window."""
        self.hb.props.title = "IV data"

        button = Gtk.Button()
        icon = Gio.ThemedIcon(name="view-refresh-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        button.set_tooltip_text("Click to refresh canvas.")
        button.connect("clicked", self.on_refresh)
        self.hb.pack_end(button)

        # Button to upload
        button = Gtk.Button()
        icon = Gio.ThemedIcon(name="document-send-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        button.set_tooltip_text("Click to upload test")
        button.connect("clicked", self.do_upload)
        self.hb.pack_end(button)

        # File entry and search button
        self.single_file = Gtk.FileChooserButton()
        self.single_file.connect("file-set", self.on_single_file_set)

        self.double_file = Gtk.FileChooserButton()
        self.double_file.connect("file-set", self.on_double_file_set)

        self.single_SN = Gtk.Label(label="(None)")
        self.double_SN = Gtk.Label(label="(None)")

        grid = Gtk.Grid(column_spacing=5, row_spacing=1)

        grid.attach(Gtk.Label(label="Files"), 1, 0, 1, 1)
        grid.attach(Gtk.Label(label="Serial No."), 2, 0, 1, 1)

        grid.attach(Gtk.Label(label="Single Data File"), 0, 1, 1, 1)
        grid.attach(self.single_file, 1, 1, 1, 1)
        grid.attach(self.single_SN, 2, 1, 1, 1)

        grid.attach(Gtk.Label(label="Double Data File"), 0, 2, 1, 1)
        grid.attach(self.double_file, 1, 2, 1, 1)
        grid.attach(self.double_SN, 2, 2, 1, 1)

        #btn = Gtk.Button(label="Compute difference")
        #btn.connect("clicked", self.on_difference)
        #grid.attach(btn, 1, 3, 1, 1)

        btn = Gtk.Button(label="Upload to DB")
        btn.connect("clicked", self.do_upload)
        grid.attach(btn, 2, 3, 1, 1)

        self.mainBox.pack_start(grid, False, True, 0)

        self.fig = mpl.figure.Figure()
        self.fig.tight_layout()
        sw = Gtk.ScrolledWindow()  # Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # A scrolled window border goes outside the scrollbars and viewport
        sw.set_border_width(10)
        sw.set_size_request(310, 310)

        self.canvas = FigureCanvas(self.fig)  # a Gtk.DrawingArea
        self.canvas.set_size_request(400, 300)
        sw.add(self.canvas)
        self.mainBox.pack_start(sw, True, True, 0)

        # Create toolbar
        try:
            toolbar = NavigationToolbar(self.canvas)
        except TypeError:
            toolbar = NavigationToolbar(self.canvas, self)

        self.mainBox.pack_start(toolbar, False, False, 0)

        # The text view
        self.mainBox.pack_start(self.message_panel.frame, True, True, 5)

        self.show_all()

    def get_difference_data(self):
        """Returns the double data witht the difference."""
        # Prepare the data
        ddata = copy.deepcopy(self.mdata["double"])

        ndata = len(self.difference)
        ddata["curve"]["V"] = np.abs(ddata["curve"]["V"][:ndata])
        ddata["curve"]["I"] = np.abs(self.difference)
        ddata["curve"]["S"] = ddata["curve"]["S"][:ndata]
        return ddata

    def upload_test(self, mdata, mod_type):
        """Upload available tests."""

        # Get JSon skeleton filled
        test = SensorUtils.sensor_data_to_json(self.session, mdata, mod_type, self)

        # write attachment.
        # First geet the fine name.
        fnam = SensorUtils.build_file_name(mdata)


        data_out = tempfile.NamedTemporaryFile("w", prefix=fnam, suffix=".dat", delete=False)
        SensorUtils.save_sensor_data(data_out, mdata, name=fnam)

        js_out = tempfile.NamedTemporaryFile("w", prefix="payload-", suffix=".json", delete=False)
        js_out.write(json.dumps(test, indent=3, cls=dbGtkUtils.MyEncoder))
        js_out.close()

        attachment = ITkDButils.Attachment(path=data_out.name, title="resultsFile", desc=fnam)
        uploadW = UploadTest.UploadTest(self.session, js_out.name, attachment)
        uploadW.connect("destroy", remove_files, [data_out.name, js_out.name])


    def do_upload(self, *args):
        """The upload button has been clicked.

        We present a dialog where we ask if the new data file should be stored
        locally and if both (single and difference) tests should be uploaded.
        """
        if "single" not in self.mdata:
            return

        if "double" not in self.mdata:
            # upload only the single test.
            if dbGtkUtils.ask_for_confirmation(
                "Uploading Single data",
                "No data for double module/sensor.\nUpload single test ?."):

                self.upload_test(self.mdata["single"], self.mod_type["single"])

            return

        # We create the dialog.
        dlg = Gtk.Dialog(title="Add Attachment", parent=self, flags=0)
        dlg.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                    Gtk.STOCK_OK, Gtk.ResponseType.OK)
        area = dlg.get_content_area()
        grid = Gtk.Grid(column_spacing=5, row_spacing=1)
        area.add(grid)

        label = Gtk.Label(label="Save locally new data file ?")
        save_locally = Gtk.Switch()
        grid.attach(label, 0, 0, 1, 1)
        grid.attach(save_locally, 1, 0, 1, 1)

        label = Gtk.Label(label="Upload both tests ?")
        do_both = Gtk.Switch()
        grid.attach(label, 0, 1, 1, 1)
        grid.attach(do_both, 1, 1, 1, 1)

        dlg.show_all()
        rc = dlg.run()
        dlg.hide()
        if rc != Gtk.ResponseType.OK:
            dlg.destroy()
            return

        mdata = self.get_difference_data()
        if save_locally.get_active():
            # Save locally.
            fnam = SensorUtils.build_file_name(mdata)
            fc = Gtk.FileChooserDialog(title="Save data file", action=Gtk.FileChooserAction.SAVE)
            fc.add_buttons(
                Gtk.STOCK_CANCEL,
                Gtk.ResponseType.CANCEL,
                Gtk.STOCK_OPEN,
                Gtk.ResponseType.OK,
            )

            if self.last_folder:
                fc.set_current_folder(self.last_folder)

            fc.set_current_name("{}.dat".format(fnam))
            rc = fc.run()
            if rc == Gtk.ResponseType.OK:
                SensorUtils.save_sensor_data(fc.get_filename(), mdata)

            fc.hide()
            fc.destroy()

        # Upload double
        self.upload_test(mdata, self.mod_type["double"])

        if do_both.get_active():
            self.upload_test(self.mdata["single"], self.mod_type["single"])

        dlg.destroy()

    def on_refresh(self, *args):
        """Refresh canvas."""
        if self.fig and self.canvas:
            self.fig.tight_layout()
            self.canvas.draw()

    def find_module(self, SN):
        """Find module (SN) on database

        Args:
            SN (str): Module Serial number.

        """
        md = ITkDButils.get_DB_component(self.session, SN)
        if md is None:
            dbGtkUtils.complain(
                "Could not find {}".format(SN), str(ITkDButils.get_db_response())
            )

        return md

    def update_folder(self, fnam):
        """Sets last folder."""

        self.last_folder = Path(fnam).parent.as_posix()
        self.single_file.set_current_folder(self.last_folder)
        self.double_file.set_current_folder(self.last_folder)

    def show_single_curve(self):
        """Shows the single curve."""
        try:
            mdata = self.mdata["single"]
        except KeyError:
            return

        is_module = is_module = "Module_SN" in mdata

        self.show_curve(
            131,
            mdata["curve"]["V"],
            mdata["curve"]["I"],
            self.mod_type["single"][0:4] if is_module else "Single",
            mdata["curve"]["labels"][0],
            mdata["curve"]["labels"][1],
        )

    def show_double_curve(self):
        """Shows the double curve."""
        try:
            mdata = self.mdata["double"]
        except KeyError:
            return

        self.show_curve(
            133,
            mdata["curve"]["V"],
            mdata["curve"]["I"],
            "Double",
            mdata["curve"]["labels"][0],
            None,
        )

    def on_single_file_set(self, *args):
        """Single sensor file chosen."""
        obj_type = ["sensor", "module"]
        fnam = self.single_file.get_filename()
        if fnam is None or not Path(fnam).exists():
            dbGtkUtils.complain("Could not find data file", fnam, parent=self)

        mdata = SensorUtils.read_sensor_file(fnam)
        self.update_folder(fnam)

        is_module = 1
        try:
            SN = mdata["Module_SN"]

        except KeyError:
            SN = mdata["Component"]
            is_module = 0

        self.write_message("Reading data for {} {}\n".format(obj_type[is_module], SN))
        md = self.find_module(SN)
        if md is None:
            self.write_message("...object does not exist.\n")
            self.single_file.unselect_all()
            return

        # All good
        self.mod_SN["single"] = SN
        self.mdata["single"] = mdata
        self.mod_type["single"] = md["type"]["code"]
        print(self.mod_type["single"])

        self.single_SN.set_text("{} - {}".format(SN, md["type"]["name"]))
        self.fig.clf()
        self.show_single_curve()

        # Compute difference if single already available
        if "double" in self.mdata:
            self.show_double_curve()
            self.on_difference()

    def check_double_SN(self, SN, is_module):
        """Check that the double SN is a good one."""
        obj_type = ["sensor", "module"]
        if "single" in self.mod_SN:
            if self.mod_SN["single"] == SN:
                dbGtkUtils.complain(
                    "Wrong SN {}".format(SN),
                    "{} already used.".format(obj_type[is_module])
                )
                self.double_file.unselect_all()
                return None

        # Check that it exists in the DB
        if len(SN) != 14 or SN[0:4] != "20US":
            self.write_message("Invalid SN: {}\n".format(SN))
            SN = dbGtkUtils.get_a_value(
                "Invalid SN", "Give Ring or corresponding Half Module SN"
            )
            return None

        md = self.find_module(SN)
        if md is None:
            self.write_message("...object does not exist.\n")
            self.double_file.unselect_all()
            return None

        return md

    def get_true_SN(self, md):
        """Get the actual SN of the 'double' object."""
        found_child = False
        has_ring = md["type"]["name"].find("Ring")
        if has_ring >= 0:
            self.write_message("...This is a Ring module. Searching children in DB\n")
            for child in md["children"]:
                if child["component"]:
                    ctype = child["type"]["code"]
                    if ctype.find("MODULE") < 0:
                        continue

                    cSN = child["component"]["serialNumber"]
                    if cSN == self.mod_SN["single"]:
                        continue

                    halfM_SN = cSN
                    found_child = True
                    self.write_message("...found {}\n".format(halfM_SN))
                    break

            if not found_child:
                self.write_message("Requesting a Half Module SN\n")
                halfM_SN = dbGtkUtils.get_a_value(
                    "Give Half Module SN", "Serial Number"
                )

            md = ITkDButils.get_DB_component(self.session, halfM_SN)
            if md is None:
                dbGtkUtils.complain(
                    "Could not find {}".format(halfM_SN),
                    str(ITkDButils.get_db_response()),
                )
                self.double_file.unselect_all()
                return None

            self.write_message("... {}\n".format(halfM_SN))
            return halfM_SN

        return md["serialNumber"]

    def on_double_file_set(self, *args):
        "File chosen for the 'double module'"
        obj_type = ["sensor", "module"]
        fnam = self.double_file.get_filename()
        if fnam is None or not Path(fnam).exists():
            dbGtkUtils.complain("Could not find data file", fnam, parent=self)

        mdata = SensorUtils.read_sensor_file(fnam)
        self.update_folder(fnam)
        is_module = 1
        # Check SN in data file
        try:
            SN = mdata["Module_SN"]
        except KeyError:
            is_module = 0
            SN = mdata["Component"]

        halfM_SN = SN
        md = self.check_double_SN(SN, is_module)
        if md is None:
            return

        self.write_message("Reading data for {} {}\n".format(obj_type[is_module], SN))
        halfM_SN = self.get_true_SN(md)
        if halfM_SN is None:
            return

        if "single" in self.mod_type:
            if is_module and self.mod_type["single"] == md["type"]["code"]:
                dbGtkUtils.complain(
                    "Wrong module type.",
                    "Module type cannot be {}".format(self.mod_type["single"]),
                )

                self.double_file.unselect_all()
                return

        self.mod_SN["double"] = halfM_SN
        self.mod_type["double"] = md["type"]["code"]
        self.mdata["double"] = mdata

        self.double_SN.set_text("{} - {}".format(halfM_SN, md["type"]["name"]))
        self.show_double_curve()

        # Compute difference if single already available
        if "single" in self.mdata:
            self.on_difference()

    def on_difference(self, *args):
        """Compute difference."""
        if "single" not in self.mdata or "double" not in self.mdata:
            dbGtkUtils.complain(
                "Data needed", "Check if single oand doubel module data are available"
            )
            return

        is_module = "Module_SN" in self.mdata["double"]
        double_I = self.mdata["double"]["curve"]["I"]
        single_I = SensorUtils.scale_iv(
            self.mdata["single"]["curve"]["I"],
            self.mdata["single"]["Temperature"] + 273.0,
            self.mdata["double"]["Temperature"] + 273.0,
        )

        try:
            nmin = double_I.size
            self.difference = double_I - single_I
        except ValueError:
            nmin = np.min([double_I.size, single_I.size])
            self.write_message(
                "Size of current arrays is not the same: {} {}\n".format(
                    double_I.size, single_I.size
                )
            )
            self.difference = double_I[:nmin] - single_I[:nmin]

        self.show_curve(
            132,
            self.mdata["double"]["curve"]["V"][:nmin],
            self.difference,
            self.mod_type["double"][0:4] if is_module else "Diff",
            self.mdata["double"]["curve"]["labels"][0],
            None,
        )

    def show_curve(self, subplot, X, Y, title=None, xlabel="X", ylabel="Y"):
        """Shows data"""
        ax = self.fig.add_subplot(subplot)
        plt.cla()
        if xlabel:
            ax.set_xlabel(xlabel)

        if ylabel:
            ax.set_ylabel(ylabel)

        if title:
            ax.set_title(title)

        ax.plot(X, Y)
        ax.grid()
        self.on_refresh()


def main():
    """Main entryy."""

    # DB login
    dlg = ITkDBlogin.ITkDBlogin()
    client = dlg.get_client()
    if client is None:
        print("Could not connect to DB with provided credentials.")
        dlg.die()
        sys.exit()

    client.user_gui = dlg

    # Start the Application
    win = IVwindow(client)
    win.show_all()
    win.set_accept_focus(True)
    win.present()
    win.connect("destroy", Gtk.main_quit)

    try:
        Gtk.main()
    except KeyboardInterrupt:
        print("Arrggggg !!!")

    dlg.die()
    print("Bye !!")
    sys.exit()

if __name__ == "__main__":
    main()
