#!/usr/bin/env python3
"""PB/Hybrid panel Visual inspection GUI.."""
import sys
import copy
from pathlib import Path

try:
    import itkdb_gtk

except ImportError:
    cwd = Path(__file__).parent.parent
    sys.path.append(cwd.as_posix())

from itkdb_gtk import dbGtkUtils, ITkDBlogin, ITkDButils, QRScanner
from itkdb_gtk.ShowComments import ShowComments
from itkdb_gtk.ShowDefects import ShowDefects
from itkdb_gtk.UploadTest import create_json_data_editor


import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, Gio, GObject


class TestJson(GObject.Object):
    """To store test JSOn."""
    __gtype_name__ = "TestJson"

    def __init__(self, js=None):
        super().__init__()
        self.js = copy.deepcopy(js)

    def set_js(self, js):
        """SEts the dictionary"""
        self.js = copy.deepcopy(js)


class PanelVisualInspection(dbGtkUtils.ITkDBWindow):
    """PB/Hybryd panel visual inspection GUI."""
    SN, ORDER, PASSED, N_FILES, F_LIST, TEST_J, ALL = range(7)
    F_DEFECT, F_NAME, F_PATH = range(3)

    def __init__(self, session, title="PanelVisualInspection", help_link=None):
        super().__init__(title=title,
                         session=session,
                         show_search="Find object with given SN.",
                         help_link=help_link)

        self.institute = self.pdb_user["institutions"][0]["code"]
        self.global_image = None
        self.global_link = None

        # action button in header
        button = Gtk.Button()
        icon = Gio.ThemedIcon(name="document-send-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        button.set_tooltip_text("Click to upload ALL tests.")
        button.connect("clicked", self.upload_tests)
        self.hb.pack_end(button)

        grid = Gtk.Grid(column_spacing=5, row_spacing=1)
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

        irow += 1
        lbl = Gtk.Label(label="Serial Number")
        lbl.set_xalign(0)
        grid.attach(lbl, 0, irow, 1, 1)

        self.SN = dbGtkUtils.TextEntry(small=True)
        self.SN.connect("text_changed", self.SN_ready)
        self.SN.widget.set_tooltip_text("Enter SN of PWD or Hybrid panel.")
        grid.attach(self.SN.widget, 1, irow, 1, 1)

        self.panel_type = Gtk.Label(label="")
        grid.attach(self.panel_type, 2, irow, 1, 1)

        irow += 1
        lbl = Gtk.Label(label="Date")
        lbl.set_xalign(0)
        grid.attach(lbl, 0, irow, 1, 1)

        self.date = dbGtkUtils.TextEntry(small=True)
        grid.attach(self.date.widget, 1, irow, 1, 1)
        self.date.entry.set_text(ITkDButils.get_db_date())
        self.date.connect("text_changed", self.new_date)

        irow += 1
        self.fC = Gtk.FileChooserButton()
        self.fC.connect("file-set", self.on_global_image)

        lbl = Gtk.Label(label="Global Image")
        lbl.set_xalign(0)
        grid.attach(lbl, 0, irow, 1, 1)
        grid.attach(self.fC, 1, irow, 1, 1)


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
        self.scanner = QRScanner.QRScanner(self.get_qrcode)

    def on_global_image(self, *args):
        """We choose the global image."""
        fnam = self.fC.get_filename()
        if fnam is None or not Path(fnam).exists():
            dbGtkUtils.complain("Could not find image", fnam, parent=self)
            return

        self.global_image = Path(fnam).expanduser().resolve()



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

    def create_model(self):
        """Create tree view model."""
        return Gtk.ListStore(str, int, bool, int, Gtk.ListStore, TestJson)

    def create_file_model(self):
        """Create model for file list"""
        return Gtk.ListStore(str, str, str)

    def create_tree_view(self, size=150):
        """Create the TreeView with the children."""
        model = self.create_model()
        self.tree = Gtk.TreeView(model=model)
        self.tree.connect("button-press-event", self.button_pressed)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.add(self.tree)
        scrolled.set_size_request(-1, size)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("SN", renderer, text=PanelVisualInspection.SN)
        self.tree.append_column(column)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("position", renderer, text=PanelVisualInspection.ORDER)
        self.tree.append_column(column)

        renderer = Gtk.CellRendererToggle()
        renderer.set_property("activatable", True)
        renderer.set_property("radio", True)
        renderer.set_padding(5, 0)

        _, y = renderer.get_alignment()
        renderer.set_alignment(0, y)
        # renderer.set_property("inconsistent", True)
        renderer.connect("toggled", self.btn_toggled)

        column = Gtk.TreeViewColumn("Passed", renderer, active=PanelVisualInspection.PASSED)
        self.tree.append_column(column)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("N. Images", renderer, text=PanelVisualInspection.N_FILES)
        self.tree.append_column(column)

        return scrolled

    def btn_toggled(self, renderer, path, *args):
        """Toggled."""
        model = self.tree.get_model()
        val = not model[path][PanelVisualInspection.PASSED]
        model[path][PanelVisualInspection.PASSED] = val


    def get_iter_at_position(self, tree, event):
        """Get the model and iterator at position."""
        # Create popup menu
        select = tree.get_selection()
        model, lv_iter = select.get_selected()
        values = None
        if lv_iter:
            values = model[lv_iter]

        else:
            P = tree.get_path_at_pos(event.x, event.y)
            if P:
                lv_iter = model.get_iter(P[0])
                values = model[lv_iter]

        return model, lv_iter, values


    def button_pressed(self, tree, event):
        """Button pressed on tree view."""
        # Create popup menu
        model, lv_iter, values = self.get_iter_at_position(tree, event)
        if not values:
            return

        # double click shows attachments
        if event.button == 1 and event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS:
            #self.write_message("This is a double click.\n")
            self.on_upload_image(None, (model, lv_iter, values))
            return

        if event.button != 3:
            return

        menu = Gtk.Menu()

        item_show = Gtk.MenuItem(label="Upload Image")
        item_show.connect("activate", self.on_upload_image, (model, lv_iter, values))
        menu.append(item_show)

        item_show_json = Gtk.MenuItem(label="Show JSOn")
        item_show_json.connect("activate", self.on_show_json, (model, lv_iter, values))
        menu.append(item_show_json)

        item_show_com = Gtk.MenuItem(label="Edit Comments")
        item_show_com.connect("activate", self.on_show_comments, (model, lv_iter, values))
        menu.append(item_show_com)

        item_show_def = Gtk.MenuItem(label="Edit Defects")
        item_show_def.connect("activate", self.on_show_defects, (model, lv_iter, values))
        menu.append(item_show_def)

        menu.show_all()
        menu.popup_at_pointer(event)

    def on_upload_image(self, item, data):
        """Add defects with images.."""

        model, lv_iter, val = data

        irow = 0
        tree = Gtk.TreeView(model=val[self.F_LIST])
        tree.connect("button-press-event", self.on_file_pressed)

        btn = Gtk.Button(label="Add image")
        btn.set_tooltip_text("Click to add a new image.")
        btn.connect("clicked", self.on_add_image, val[PanelVisualInspection.F_LIST])

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.add(tree)
        scrolled.set_size_request(-1, 150)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Description", renderer, text=PanelVisualInspection.F_DEFECT)
        tree.append_column(column)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("File", renderer, text=PanelVisualInspection.F_NAME)
        tree.append_column(column)

        dlg = Gtk.Dialog(title="Add Image")
        dlg.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                        Gtk.STOCK_OK, Gtk.ResponseType.OK)
        box = dlg.get_content_area()
        box.add(btn)
        box.add(scrolled)
        dlg.show_all()
        rc = dlg.run()
        if rc == Gtk.ResponseType.OK:
            f_model = tree.get_model()
            n_files = f_model.iter_n_children()
            model.set_value(lv_iter, PanelVisualInspection.F_LIST, f_model)
            model.set_value(lv_iter, PanelVisualInspection.N_FILES, n_files)

        dlg.hide()
        dlg.destroy()

        self.write_message("Defects added\n")

    def on_file_pressed(self, tree, event):
        """Called when right button clicked in add image dialog.

        Opens a pop-up menu to delete the selected entry."""
        # double click shows attachments
        if event.button == 1 and event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS:
            self.write_message("This is a double click.\n")
            return


        if event.button != 3:
            return

        model, lv_iter, values = self.get_iter_at_position(tree, event)
        if not values:
            return
        menu = Gtk.Menu()

        item_show = Gtk.MenuItem(label="Delete")
        item_show.connect("activate", self.on_delete_image, (model, lv_iter, values))
        menu.append(item_show)

        menu.show_all()
        menu.popup_at_pointer(event)

    def on_delete_image(self, item, data):
        """Delete a defect and image"""
        model, lv_iter, _ = data
        model.remove(lv_iter)

    def on_add_image(self, btn, model):
        """Adds a new image."""
        dlg = Gtk.Dialog(title="Add Image")

        dlg.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                        Gtk.STOCK_OK, Gtk.ResponseType.OK)
        box = dlg.get_content_area()
        grid = Gtk.Grid(column_spacing=5, row_spacing=1)
        box.add(grid)

        irow = 0
        lbl = Gtk.Label(label="Description")
        lbl.set_xalign(0)
        grid.attach(lbl, 0, irow, 1, 1)

        desc = Gtk.Entry()
        grid.attach(desc, 1, irow, 1, 1)

        irow += 1
        lbl = Gtk.Label(label="Image")
        lbl.set_xalign(0)
        grid.attach(lbl, 0, irow, 1, 1)

        fC = Gtk.FileChooserButton()
        grid.attach(fC, 1, irow, 1, 1)

        dlg.show_all()

        rc = dlg.run()
        if rc == Gtk.ResponseType.OK:
            D = desc.get_text()
            P = Path(fC.get_filename()).expanduser().resolve()
            model.append([D, P.name, P.as_posix()])

        dlg.hide()
        dlg.destroy()

    def on_show_json(self, item, data):
        """Test JSon."""
        model, lv_iter, val = data
        payload = val[PanelVisualInspection.TEST_J].js
        value, dlg = create_json_data_editor(payload)
        rc = dlg.run()
        if rc == Gtk.ResponseType.OK:
            payload = value.values
            model.set_value(lv_iter, PanelVisualInspection.TEST_J, TestJson(payload))

        dlg.hide()
        dlg.destroy()

    def on_show_comments(self, item, data):
        """Show comments"""
        model, lv_iter, val = data
        js = val[PanelVisualInspection.TEST_J].js
        SC = ShowComments("Test Comments", js["comments"], self)
        rc = SC.run()
        if rc == Gtk.ResponseType.OK:
            js["comments"] = SC.comments
            model.set_value(lv_iter, PanelVisualInspection.TEST_J, TestJson(js))

        SC.hide()
        SC.destroy()

    def on_show_defects(self, item, data):
        """Show comments"""
        model, lv_iter, val = data
        js = val[PanelVisualInspection.TEST_J].js
        SD = ShowDefects("Test Defects", js["defects"], self)
        rc = SD.run()
        if rc == Gtk.ResponseType.OK:
            js["defects"] = SD.defects
            model.set_value(lv_iter, PanelVisualInspection.TEST_J, TestJson(js))

        SD.hide()
        SD.destroy()

    def SN_ready(self, *args):
        """SN is ready in the TextEnttry."""
        SN = self.SN.get_text()
        # GEt children.
        panel = ITkDButils.get_DB_component(self.session, SN)
        if panel is None:
            self.write_message(ITkDButils.get_db_response())
            return

        SN = panel["serialNumber"]
        args[0].set_text(SN)
        is_PWB = False
        defaults = {
            "institution": self.institute,
            "runNumber": "1",
            "date": self.date.get_text()
        }
        component_type = None
        test_code = None
        if "USED" in SN:
            # Powerboard Carrier
            if not SN[6].isdigit():
                dbGtkUtils.complain("Not a Powerboard Carrier",
                                    "{}: wrong SN for a powerboard carrier".format(SN))
                self.SN.widget.set_text("")
                return

            self.panel_type.set_text("PWB carrier")
            is_PWB = True
            component_type = "PWB"
            test_code = "PICTURE"

        elif "USET" in SN:
            # Hybrid test panel
            component_type = "HYBRID_TEST_PANEL"
            test_code = "VISUAL_INSPECTION"

            if not SN[6].isdigit or int(SN[6])>5:
                dbGtkUtils.complain("Not a Hybrid Test Panel",
                                    "{}: wrong SN for a hybrid test panel".format(SN))
                self.SN.widget.set_text("")
                return

            self.panel_type.set_text("HYB test panel")

        else:
            dbGtkUtils.complain("Invalid SN.",
                "{}\nNot a PWB carrier not HYB test panel.".format(SN))
            self.SN.widget.set_text("")
            return

        # GEt children.
        skltn = ITkDButils.get_test_skeleton(self.session, component_type, test_code, defaults)
        model = self.create_model()
        for child in panel["children"]:
            if child["component"] is not None:
                child_SN = child["component"]["serialNumber"]
                skltn["component"] = child_SN
                if is_PWB:
                    position = child["order"]
                else:
                    position = -1
                    for P in child["properties"]:
                        if P["code"] == "HYBRID_POSITION":
                            if P["value"] is not None:
                                position = int(P["value"])
                                break

                model.append([child_SN, position, True, 0, self.create_file_model(), TestJson(skltn)])

        self.tree.set_model(model)


    def upload_tests(self, *args):
        """Upload the current test."""
        SN = self.SN.get_text()

        model = self.tree.get_model()
        lv_iter = model.get_iter_first()
        n_items = 0
        global_link = None
        while lv_iter:
            values = model[lv_iter]
            payload = values[PanelVisualInspection.TEST_J].js

            attachments = []
            if global_link is None:
                A = ITkDButils.Attachment(path=self.global_image, title="Global Image", desc="Image of whole panel")
                attachments.append(A)

            im_model = values[PanelVisualInspection.F_LIST]
            im_iter = im_model.get_iter_first()
            idef = 1
            while im_iter:
                defect, name, path = im_model[im_iter]
                A = ITkDButils.Attachment(path=path, title="Defect {}".format(idef), desc=defect)
                attachments.append(A)
                idef += 1
                im_iter = im_model.iter_next(im_iter)

            rc = ITkDButils.upload_test(self.session, payload, attachments, check_runNumber=True)
            if rc:
                ipos = rc.find("The following details may help:")
                msg = rc[ipos:]
                dbGtkUtils.complain("Failed uploading test {}-{}".format(payload["component"], payload["testType"]), msg)
                self.write_message(msg+"\n")

            else:
                self.write_message("Upload {}-{} successfull\n".format(payload["component"], payload["testType"]))
                if global_link is None:
                    try:
                        global_link = ITkDButils.attachment_urls[self.global_image.name]
                    except KeyError:
                        pass

                if payload["testType"] == "PICTURE":
                    rc = ITkDButils.set_test_run_parameter(self.session,
                                                           ITkDButils.uploaded_test_runs[0],
                                                           "COMMENT", "Picture of PW carrier")

                    rc = ITkDButils.set_test_run_parameter(self.session,
                                                           ITkDButils.uploaded_test_runs[0],
                                                           "LINK_TO_PICTURE", global_link)
                    if rc:
                        ipos = rc.find("The following details may help:")
                        msg = rc[ipos:]
                        dbGtkUtils.complain("Failed updating LINK_TO_PICTURE {}-{}".format(payload["component"],
                                                                                           payload["testType"]), msg)
                        self.write_message(msg+'\n')

                elif payload["testType"] == "VISUAL_INSPECTION":
                    rc = ITkDButils.create_test_run_comment(self.session,
                                                            ITkDButils.uploaded_test_runs[0],
                                                            ["Link to global image:\n {}".format(global_link)])
                    if rc:
                        ipos = rc.find("The following details may help:")
                        msg = rc[ipos:]
                        dbGtkUtils.complain("Failed adding global link as comment: {}-{}".format(payload["component"],
                                                                                                 payload["testType"]), msg)
                        self.write_message(msg+"\n")
                    else:
                        self.write_message("Image: {}\n".format(global_link))


            n_items += 1
            lv_iter = model.iter_next(lv_iter)


    def get_qrcode(self,txt):
        """Read SN from scanner."""
        self.write_message("SN: {}\n".format(txt))
        self.SN_ready(txt, self.SN.widget)


def main():
    """Main entry."""
    # DB login
    HELP_LINK="https://itkdb-gtk.docs.cern.ch/panelVisualInspection.html"

    dlg = ITkDBlogin.ITkDBlogin()
    client = dlg.get_client()
    if client is None:
        print("Could not connect to DB with provided credentials.")
        dlg.die()
        sys.exit()

    client.user_gui = dlg

    gTest = PanelVisualInspection(client, help_link=HELP_LINK)

    gTest.present()
    gTest.connect("destroy", Gtk.main_quit)
    try:
        Gtk.main()

    except KeyboardInterrupt:
        print("Arrrgggg!!!")

    dlg.die()

if __name__ == "__main__":
    main()
