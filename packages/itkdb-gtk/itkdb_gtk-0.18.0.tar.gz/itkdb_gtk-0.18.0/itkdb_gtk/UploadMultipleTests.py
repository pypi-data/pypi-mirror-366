#!/usr/bin/env python3
"""GUI to upload tests."""
import fnmatch
import json
import os
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
from itkdb_gtk.UploadTest import create_json_data_editor

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio, Gdk

# Check if Gtk can be open
gtk_runs, gtk_args = Gtk.init_check()


def handle_test_date(the_date):
    """Edit date."""
    the_date = the_date[:19].replace('T', ' ')
    return the_date


def all_files(root, patterns='*', single_level=False, yield_folders=False):
    """A generator that reruns all files in the given folder.

    Args:
        root (file path): The folder
        patterns (str, optional): The pattern of the files. Defaults to '*'.
        single_level (bool, optional): If true, do not go into sub folders. Defaults to False.
        yield_folders (bool, optional): If True, return folders as well. Defaults to False.

    Yields:
        str: file path name

    """
    patterns = patterns.split(';')
    for path, subdirs, files in os.walk(root):
        if yield_folders:
            files.extend(subdirs)

        files.sort()
        for name in files:
            for pattern in patterns:
                if fnmatch.fnmatch(name, pattern):
                    yield os.path.join(path, name)
                    break

        if single_level:
            break


class TestList(object):
    """Enumeration with TreeView model columns."""
    (
        SN,
        TestType,
        RunNumber,
        Date,
        Institute,
        Stage,
        currentStage,
        Path,
        Json,
        Nattch,
        Attachments,
        Ncomm,
        Comments,
        Ndef,
        Defects,
        Color,
        ALL,
    ) = range(17)


def check_data(data):
    """Checks validity of JSon data.

    Args:
        data (): The json data

    Returns:
    -------
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


class UploadMultipleTests(dbGtkUtils.ITkDBWindow):
    """Collects information to upload a test and its attachments."""

    def __init__(self, session, help_link=None):
        """Initialization.

        Args:
            session: ITkDB session

        """
        super().__init__(session=session, title="Upload Tests", gtk_runs=gtk_runs, help_link=help_link)
        self.tests = []
        self.data = None
        self.tree = None
        self.is_retroactive = False
        self.def_color = None

        self.init_window()

    def init_window(self):
        """Creates the Gtk window."""
        # Initial tweaks
        self.set_border_width(10)

        # Prepare HeaderBar
        self.hb.props.title = "Upload Multiple Tests"

        # Active buttin in header
        button = Gtk.Button()
        icon = Gio.ThemedIcon(name="document-send-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        button.set_tooltip_text("Click to upload test")
        button.connect("clicked", self.upload_test_gui)
        self.hb.pack_end(button)

        # Data panel
        grid = Gtk.Grid(column_spacing=5, row_spacing=1)
        self.mainBox.pack_start(grid, False, False, 0)

        # The test file widgets
        lbl = Gtk.Label(label="Select Test Files: ")
        lbl.set_xalign(0)
        grid.attach(lbl, 0, 0, 1, 1)

        btn = Gtk.Button()
        icon = Gio.ThemedIcon(name="text-x-generic-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        btn.add(image)
        btn.set_tooltip_text("Click to select multiple tests.")
        btn.connect("clicked", self.on_select_test)
        grid.attach(btn, 1, 0, 1, 1)

        btn = Gtk.Button()
        icon = Gio.ThemedIcon(name="folder-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        btn.add(image)
        btn.set_tooltip_text("Click to select a folder to scan.")
        btn.connect("clicked", self.on_select_folder)
        grid.attach(btn, 2, 0, 1, 1)

        # toggle = Gtk.ToggleButton("RetroActive")
        # toggle.set_tooltip_text("Toggle to make all uploads retroactive.")
        # toggle.connect("toggled", self.on_toggle_retroactive)
        # grid.attach(toggle, 3, 0, 1, 1)

        # Paned object
        paned = Gtk.Paned(orientation=Gtk.Orientation.VERTICAL)
        paned.set_size_request(-1, 200)
        self.mainBox.pack_start(paned, True, True, 5)

        # the list of attachments
        tree_view = self.create_tree_view()
        paned.add1(tree_view)

        # The text view
        paned.add2(self.message_panel.frame)

        self.show_all()

    def create_tree_view(self, size=150):
        """Creates the tree vew with the attachments."""
        model = Gtk.ListStore(str, # SN
                              str, # test type
                              str, # runNumber
                              str, # date
                              str, # institute
                              str, # stage
                              str, # stage
                              str, # ifile
                              object, # data
                              int, # num. attch.
                              object, # attachments
                              int, # num. comments
                              object, # comments
                              int, # num defects
                              object, # defects
                              str # color
                              )
        self.tree = Gtk.TreeView(model=model)
        self.tree.connect("button-press-event", self.button_pressed)
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.add(self.tree)
        scrolled.set_size_request(-1, size)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("SN", renderer, text=TestList.SN)
        self.tree.append_column(column)

        renderer = Gtk.CellRendererText()
        self.def_color = renderer.get_property("foreground-rgba").to_string()
        column = Gtk.TreeViewColumn("Test Type", renderer, text=TestList.TestType, foreground=TestList.Color)
        self.tree.append_column(column)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Run", renderer, text=TestList.RunNumber)
        self.tree.append_column(column)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Institute", renderer, text=TestList.Institute)
        self.tree.append_column(column)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Stage", renderer, text=TestList.Stage)
        self.tree.append_column(column)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("N. att.", renderer, text=TestList.Nattch)
        self.tree.append_column(column)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("N. comm.", renderer, text=TestList.Ncomm)
        self.tree.append_column(column)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("N. def.", renderer, text=TestList.Ndef)
        self.tree.append_column(column)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Date", renderer, text=TestList.Date)
        self.tree.append_column(column)

        return scrolled

    def button_pressed(self, tree, event):
        """Button pressed on tree view."""
        # double click shows attachments
        if event.button == 1 and event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS:
            select = self.tree.get_selection()
            model, lv_iter = select.get_selected()
            if not lv_iter:
                return

            self.on_show_json(None, (model, lv_iter, model[lv_iter]))
            # self.on_show_attachments(None, (model, lv_iter, model[lv_iter]))
            return

        if event.button != 3:
            return

        # Create popup menu
        select = self.tree.get_selection()
        model, lv_iter = select.get_selected()
        values = None
        if lv_iter:
            values = model[lv_iter]

        if not lv_iter:
            P = tree.get_path_at_pos(event.x, event.y)
            if P:
                print(P[0].to_string())
                lv_iter = model.get_iter(P[0])
                values = model[lv_iter]

        if not values:
            return

        menu = Gtk.Menu()
        item_show = Gtk.MenuItem(label="Show JSOn")
        item_show.connect("activate", self.on_show_json, (model, lv_iter, values))
        menu.append(item_show)

        item_set_stage = Gtk.MenuItem(label="Set Stage")
        item_set_stage.connect("activate", self.on_set_stage, (model, lv_iter, values))
        menu.append(item_set_stage)

        item_show_att = Gtk.MenuItem(label="Edit Attachments")
        item_show_att.connect("activate", self.on_show_attachments, (model, lv_iter, values))
        menu.append(item_show_att)

        item_show_com = Gtk.MenuItem(label="Edit Comments")
        item_show_com.connect("activate", self.on_show_comments, (model, lv_iter, values))
        menu.append(item_show_com)

        item_show_def = Gtk.MenuItem(label="Edit Defects")
        item_show_def.connect("activate", self.on_show_defects, (model, lv_iter, values))
        menu.append(item_show_def)

        item_del = Gtk.MenuItem(label="Delete")
        item_del.connect("activate", self.on_delete_tests, (model, lv_iter, values))
        menu.append(item_del)
        menu.show_all()

        menu.popup_at_pointer(event)

    def on_toggle_retroactive(self, toggle, *args):
        """Called when retroactive button is toggled."""
        self.is_retroactive = toggle.get_active()
        print("Is retroactive", self.is_retroactive)

    def on_show_json(self, item, data):
        """Test JSon."""
        model, lv_iter, val = data
        payload = val[TestList.Json]
        value, dlg = create_json_data_editor(payload)
        rc = dlg.run()
        if rc == Gtk.ResponseType.OK:
            payload = value.values
            model.set_value(lv_iter, TestList.Json, payload)
            model.set_value(lv_iter, TestList.SN, payload["component"])
            model.set_value(lv_iter, TestList.RunNumber, payload["runNumber"])
            model.set_value(lv_iter, TestList.Date, handle_test_date(payload["date"]))
            model.set_value(lv_iter, TestList.Institute, handle_test_date(payload["institution"]))

        dlg.hide()
        dlg.destroy()

    def on_show_attachments(self, item, data):
        """Show the attachmetns."""
        model, lv_iter, val = data

        SA = ShowAttachments("Test Attachments", self.session, val[TestList.Attachments], parent=self)
        response = SA.run()
        if response == Gtk.ResponseType.OK:
            model.set_value(lv_iter, TestList.Attachments, SA.attachments)
            model.set_value(lv_iter, TestList.Nattch, len(SA.attachments))

        SA.hide()
        SA.destroy()

    def on_show_comments(self, item, data):
        """Show comments"""
        model, lv_iter, val = data
        SC = ShowComments("Test Comments", val[TestList.Comments], self)
        rc = SC.run()
        if rc == Gtk.ResponseType.OK:
            model.set_value(lv_iter, TestList.Comments, SC.comments)
            model.set_value(lv_iter, TestList.Ncomm, len(SC.comments))

        SC.hide()
        SC.destroy()

    def on_show_defects(self, item, data):
        """Show comments"""
        model, lv_iter, val = data
        SD = ShowDefects("Test Defects", val[TestList.Defects], self)
        rc = SD.run()
        if rc == Gtk.ResponseType.OK:
            model.set_value(lv_iter, TestList.Defects, SD.defects)
            model.set_value(lv_iter, TestList.Ndef, len(SD.defects))

        SD.hide()
        SD.destroy()

    def on_delete_tests(self, item, data):
        """Test edit."""
        model, lv_iter, val = data
        rc = dbGtkUtils.ask_for_confirmation("Remove this test?",
                                             "{} - {}".format(val[TestList.SN], val[TestList.TestType]))
        if rc:
            model.remove(lv_iter)

    def get_test_institute(self):
        """Select an institue."""
        dlg = Gtk.Dialog(title="Select Institution.", flags=0)
        dlg.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                        Gtk.STOCK_OK, Gtk.ResponseType.OK)
        area = dlg.get_content_area()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        area.add(box)

        box.pack_start(Gtk.Label(label="Select an Institute"), False, True, 0)

        combo = self.create_institute_combo(only_user=True)
        box.pack_start(combo, False, True, 5)

        btn = Gtk.CheckButton(label="Use as default for other tests missing institute ?")
        box.pack_start(btn, False, True, 5)
        dlg.show_all()
        rc = dlg.run()

        out = None
        if rc == Gtk.ResponseType.OK:
            out = self.get_institute_from_combo(combo)

        use_default = btn.get_active()
        dlg.hide()
        dlg.destroy()
        return out, use_default

    def on_set_stage(self, item, data):
        """Set the test stage."""
        model, lv_iter, val = data
        SN = val[TestList.SN]
        combo, _ = self.get_component_stages(SN)

        dlg = Gtk.Dialog(title="Set object stage")

        dlg.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                        Gtk.STOCK_OK, Gtk.ResponseType.OK)
        area = dlg.get_content_area()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        area.add(box)

        box.pack_start(Gtk.Label(label="Select Stage"), False, True, 0)
        box.pack_start(combo, False, True, 0)
        toggle = Gtk.ToggleButton("Retroactive")
        box.pack_start(toggle, False, True, 0)

        dlg.show_all()

        rc = dlg.run()
        if rc == Gtk.ResponseType.OK:
            new_stage = combo.get_active_text()
            model[lv_iter][TestList.Stage] = new_stage
            data = model[lv_iter][TestList.Json]
            if toggle.get_active():
                data["isRetroactive"] = True
                data["stage"] = new_stage

            else:
                changed = (new_stage != model[lv_iter][TestList.currentStage])
                data["isRetroactive"] = changed
                if changed:
                    data["stage"] = new_stage
                else:
                    if "stage" in data:
                        del data["stage"]

            model[lv_iter][TestList.Json] = data

        dlg.hide()
        dlg.destroy()

    def get_component_stages(self, SN):
        """Create a combo with the stages."""
        try:
            obj = ITkDButils.get_DB_component(self.session, SN)
            currentStage = obj["currentStage"]["code"]

            combo = Gtk.ComboBoxText.new_with_entry()
            combo.remove_all()
            indx = 0
            for i, stg in enumerate(obj["stages"]):
                S = stg["code"]
                combo.append_text(S)
                if S == currentStage:
                    indx = i

            combo.set_active(indx)
            return combo, currentStage

        except Exception:
            self.write_message("Something went wrong with the stages\n")
            return [None, None]

    def add_test_data_to_view(self, data, default_site=None, use_default=False, ifile=None, folder=None):
        """Add a test data to the  tree view."""
        has_errors = False
        errors, missing = check_data(data)
        if len(missing) > 0:
            self.write_message("Some keys are missing in the JSon file.\n")
            self.write_message("{}\n".format("\n".join(['\t'+line for line in missing])))

            if "institution" in missing and len(missing) == 1:
                if default_site is None:
                    site, use_default = self.get_test_institute()
                    if use_default:
                        default_site = site
                else:
                    site = default_site

                if site:
                    data["institution"] = site
                    self.write_message("Setting Institution to {}\n".format(data["institution"]))

            else:
                has_errors = True
                dbGtkUtils.complain("Invalid JSON file\n{}".format('\n'.join(errors)),"--")

        if not has_errors:
            attachments = []
            if "attachments" in data:
                for att in data["attachments"]:
                    path = Path(att["path"])
                    if path.exists():
                        path = path.expanduser().resolve()
                    else:
                        if folder is not None:
                            path = folder / path.name

                    if path.exists():
                        attachments.append(ITkDButils.Attachment(path=path,
                                                                 title=att["title"],
                                                                 desc=att["description"]))
                    else:
                        self.write_message("Ignoring atachment {}".format(data["path"]))

                # We need to delete this, which is "unofficial"
                del data["attachments"]

            model = self.tree.get_model()
            comments = data.get("comments", [])
            defects = data.get("defects", [])
            the_date = handle_test_date(data["date"])
            combo, currentStage = self.get_component_stages(data["component"])
            if data["passed"]:
                if data["problems"]:
                    color = "orange"
                else:
                    color = self.def_color
            else:
                color = "firebrick"

            model.append([data["component"], data["testType"], data["runNumber"], the_date,
                            data["institution"], currentStage, currentStage,
                            ifile, data, len(attachments), attachments,
                            len(comments), comments, len(defects), defects, color])

        return default_site, use_default

    def add_tests_to_view(self, files):
        """Add the input fiels to the treeview."""
        default_site = None
        use_default = False
        for ifile in files:
            try:
                self.write_message("{}\n".format(Path(ifile).name))
                folder = Path(ifile).parent

                data = json.loads(open(ifile, "r", encoding="UTF-8").read())
                default_site, use_default = self.add_test_data_to_view(
                    data,
                    default_site=default_site,
                    use_default=use_default,
                    ifile=ifile,
                    folder=folder,
                )

            except Exception as E:
                self.write_message("Cannot load file {}\n".format(ifile))
                self.write_message("{}\n".format(str(E)))

    def on_select_folder(self, *args):
        """Caalback for select folder button"""
        fdlg = Gtk.FileChooserNative(action=Gtk.FileChooserAction.SELECT_FOLDER, accept_label="Select")
        response = fdlg.run()
        if response == Gtk.ResponseType.ACCEPT:
            folder = fdlg.get_filename()
            ifiles = [ipath for ipath in all_files(folder, '*.json')]
            self.add_tests_to_view(ifiles)

        fdlg.hide()
        fdlg.destroy()

    def on_select_test(self, *args):
        """Test file browser clicked."""
        fdlg = Gtk.FileChooserNative(action=Gtk.FileChooserAction.OPEN, accept_label="Select")

        filter_js = Gtk.FileFilter()
        filter_js.set_name("JSon files")
        filter_js.add_mime_type("application/json")
        fdlg.add_filter(filter_js)

        filter_any = Gtk.FileFilter()
        filter_any.set_name("Any files")
        filter_any.add_pattern("*")
        fdlg.add_filter(filter_any)

        fdlg.set_select_multiple(True)

        response = fdlg.run()
        if response == Gtk.ResponseType.ACCEPT:
            ifiles = [ipath for ipath in fdlg.get_filenames()]
            self.add_tests_to_view(ifiles)

        fdlg.hide()
        fdlg.destroy()
        return

    def show_data(self, *args):
        """Show data button clicked."""
        if self.data is None:
            return

        dlg = Gtk.Dialog(title="Test Data")
        dlg.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                        Gtk.STOCK_OK, Gtk.ResponseType.OK)

        dlg.set_property("height-request", 500)
        box = dlg.get_content_area()
        value = dbGtkUtils.DictDialog(self.data)
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.add(value)
        box.pack_start(scrolled, True, True, 10)

        dlg.show_all()

        rc = dlg.run()
        if rc == Gtk.ResponseType.OK:
            self.data = value.values

        dlg.hide()
        dlg.destroy()

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

    def upload_test_gui(self, *args):
        """Uploads test and attachments."""
        self.upload_test()

    def upload_test(self):
        """Uploads tests and attachments."""
        model = self.tree.get_model()
        lv_iter = model.get_iter_first()
        ngood = 0
        nbad = 0
        while lv_iter:
            past_iter = None
            values = model[lv_iter]
            payload = values[TestList.Json]
            payload["comments"] = values[TestList.Comments]
            payload["defects"] = values[TestList.Defects]

            rc = ITkDButils.upload_test(self.session, payload, values[TestList.Attachments], check_runNumber=True)
            if rc:
                ipos = rc.find("The following details may help:")
                if ipos>=0:
                    msg = rc[ipos:]
                else:
                    msg = rc
                dbGtkUtils.complain("Failed uploading test {}-{}\n".format(payload["component"], payload["testType"]), msg)
                self.write_message("Failed uploading test {}-{}\n{}\n".format(payload["component"], payload["testType"], msg))
                nbad += 1

            else:
                self.write_message("Upload {}-{} successfull\n".format(payload["component"], payload["testType"]))
                past_iter = lv_iter
                ngood += 1

            lv_iter = model.iter_next(lv_iter)
            if past_iter:
                model.remove(past_iter)

        if nbad>0:
            dbGtkUtils.complain("Failed to upload some tests", "{}/{} tests had errors.\nThey are left in the ListView.".format(nbad, ngood))
        else:
            dbGtkUtils.complain("All {} tests uploaded succesfully".format(ngood))


def main():
    """Main entry."""
    HELP_LINK="https://itkdb-gtk.docs.cern.ch/uploadMultipleTests.html"
    # DB login
    dlg = ITkDBlogin.ITkDBlogin()
    client = dlg.get_client()
    if client is None:
        print("Could not connect to DB with provided credentials.")
        dlg.die()
        sys.exit()

    client.user_gui = dlg

    # Start GUI
    UpT = UploadMultipleTests(client, help_link=HELP_LINK)

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
