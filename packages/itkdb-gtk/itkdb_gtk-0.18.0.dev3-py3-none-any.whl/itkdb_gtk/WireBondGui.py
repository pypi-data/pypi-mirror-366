#!/usr/bin/env python3
"""Wirebonding GUI for PSB."""

import sys
import re
import json
import copy
from pathlib import Path
from collections import namedtuple
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio, Gdk

try:
    import itkdb_gtk

except ImportError:
    cwd = Path(__file__).parent.parent
    sys.path.append(cwd.as_posix())
    import itkdb_gtk

__HELP_LINK__="https://itkdb-gtk.docs.cern.ch/wirebondTest.html"

from itkdb_gtk import dbGtkUtils
from itkdb_gtk import ITkDBlogin, ITkDButils, UploadTest


#valid_channel = re.compile("(^[0-9]+)-([0-9]+)")
valid_channel = re.compile("^[0-9]+[\\s*\\,\\s,-[0-9]+]*")


test_parameters = {
        "Repaired Row 1": "REPAIRED_FRONTEND_ROW1",
        "Failed Row 1": "FAILED_FRONTEND_ROW1",
        "Repaired Row 2": "REPAIRED_FRONTEND_ROW2",
        "Failed Row 2": "FAILED_FRONTEND_ROW2",
        "Repaired Row 3": "REPAIRED_FRONTEND_ROW3",
        "Failed Row 3": "FAILED_FRONTEND_ROW3",
        "Repaired Row 4": "REPAIRED_FRONTEND_ROW4",
        "Failed Row 4": "FAILED_FRONTEND_ROW4",
        "Repaired Hyb->PB": "REPAIRED_HYBRID_TO_PB",
        "Failed HyB->PB": "FAILED_HYBRID_TO_PB",
        "Repaired Module->Frame": "REPAIRED_MODULE_TO_FRAME",
        "Failed Module->Frame": "FAILED_MODULE_TO_FRAME"
}

# module_param[iring][i_sensor][i_hybrid][i_row]
module_param = {
    0: [
        [
            [[255, 830], [1343, 1918], [2431, 3006], [3519, 4094]],
            [[831, 1342], [1919, 2430], [3007, 3518], [4095, 4606]],
        ]
    ],
    1: [
        [
            [[271, 974], [1615, 2318], [2959, 3662], [4303, 5006]],
            [[975, 1614], [2319, 2958], [3663, 4302], [5007, 5646]],
        ]
    ],
    2: [
        [
            [[201, 968], [969, 1736], [1737, 2504], [2505, 3272]]
        ]
    ],
    3: [
        [
            [[566, 1013], [2358, 2805], [4150, 4597], [5942, 6389]],
            [[1462, 1909], [3254, 3701], [5046, 5493], [6838, 7285]]
        ],
        [
            [[1014, 1461], [2806, 3253], [4598, 5045], [6390, 6837]],
            [[1910, 2357], [3702, 4149], [5494, 5941], [7286, 7733]]
        ]
    ],
    4: [
        [
            [[318, 829], [1342, 1853], [2366, 2877], [3390, 3901]]
        ],
        [
            [[830, 1341], [1854, 2365], [2878, 3389], [3902, 4413]]
        ]
    ],
    5: [
        [
            [[332, 907], [1484, 2059], [2636, 3211], [3788, 4363]]
        ],
        [
            [[908, 1483], [2060, 2635], [3212, 3787], [4364, 4939]]
        ]
    ],
}

module_to_tf = {
    0: [],
    1: [],
    2: [],
    3: [],
    4: [],
    5: []
}

hyb_to_pb = {
    0: [],
    1: [],
    2: [],
    3: [],
    4: [],
    5: []
}


def range_to_list(V):
    """Convert a range to a list.

        ch1-ch2 or ch1:ch2 -> [ch1, ch1+1, ch1+2, ..., ch2] or
        ch1:step:ch2 -> [ch1, ch1+sep, ch1+2*step, ..., ch2]
    """
    nfound = 0
    for c in "-:,":
        if c in V:
            nfound += 1
            break

    if nfound == 0:
        return [V]

    out = []
    values = V.split(',')
    for V in values:
        if '-' in V:
            endpoints = list(map(int, V.split('-')))
            endpoints.sort()
            for i in range(endpoints[0], endpoints[1]+1):
                out.append(str(i))
        elif ':' in V:
            endpoints = list(map(int, V.split(':')))
            if len(endpoints) == 2:
                endpoints.sort()
                for i in range(endpoints[0], endpoints[1]+1):
                    out.append(str(i))

            elif len(endpoints) == 3:
                for i in range(endpoints[0], endpoints[2]+1, endpoints[1]):
                    out.append(str(i))

            else:
                print("Wring range specification. {}".format(V))
                continue

        else:
            out.append(V)

    return out

def count_items(items):
    """Count number of channels from results."""
    nitems = 0
    for key in items.keys():
        nitems += len(range_to_list(key))

    return nitems

def find_holes(chan_list, min_chan=0, max_chan=999999):
    """Find groups of consecutive channels."""
    out = sorted(chan_list)
    nchan = 0
    last_chan = -1
    ichan = -1
    holes = []
    for chan in out:
        if chan < min_chan or chan > max_chan:
            continue

        if last_chan < 0:
            last_chan = chan
            continue

        if chan - last_chan > 1:
            if nchan:
                holes.append([ichan, nchan])
            nchan = 0
            ichan = -1
        else:
            if last_chan < max_chan and chan >= max_chan:
                # WE are in another sensor
                holes.append([ichan, nchan])
                nchan = 0
                ichan = -1
                last_chan = chan
                continue

            nchan += 1
            if ichan < 0:
                ichan = last_chan
                nchan += 1

        last_chan = chan

    if nchan:
        holes.append([ichan, nchan])

    return holes


def wire2strip(iwire, irow, first_chan):
    """From bond to strip number."""
    if irow % 2:
        istrip = 2*(iwire-first_chan) + 1
    else:
        istrip = 2*(iwire-first_chan)

    return istrip


class Hole:
    """A range of consecutive unconnected channels."""
    def __init__(self, *args):
        for i, name in enumerate(['sensor', 'hybrid', 'row', 'chan', 'width']):
            setattr(self, name, args[i])

    def __repr__(self):
        return "sensor: {} hyb: {} row: {} chan: {} width: {}".format(
            self.sensor, self.hybrid, self.row, self.chan, self.width
        )

class HybridHoles:
    """Holes in hybrid bonds.

    Holes are defined by a list [first_chan, n_chan].
    """

    def __init__(self, param, win=None, hid=0):
        """Initialization.

        Args:
            param: Hybrid wirebon parameters.

        """
        self.win = win
        self.id = hid
        self.param = param
        self.nchan = 0
        for min_chan, max_chan in param:
            self.nchan += (max_chan-min_chan+1)

        self.holes = [[] for irow in range(4)]
        self.channels = [[] for irow in range(4)]
        # Sensor strips for each of the strip rows "served" by a hybrid.
        self.sensor_channels = [[], []]
        self.sensor_holes = [[], []]

    def ready(self):
        """Call when all channels are in."""
        for irow, C in enumerate(self.channels):
            C.sort()
            self.holes[irow] = find_holes(C)

        for irow, S in enumerate(self.sensor_channels):
            S.sort()
            self.sensor_holes[irow] = find_holes(S)

    def add_channel(self, irow, ichan)->bool:
        """Add a new channel in row.

        Args:
            irow: row number
            ichan: channel number

        Returns:
            True if added, False otherwise.

        """
        first_chan = self.param[irow][0]
        last_chan = self.param[irow][1]
        strip_row = int(irow/2)


        if isinstance(ichan, list) or isinstance(ichan, tuple):
            nadded = 0
            for ich in ichan:
                if first_chan <= ich <= last_chan:
                    self.channels[irow].append(ich)
                    nadded += 1

            self.channels[irow] = sorted(self.channels[irow])
            for iwire in self.channels[irow]:
                istrip = wire2strip(iwire, irow, first_chan)
                self.sensor_channels[strip_row].append(istrip)

            return nadded>0

        if first_chan <= ichan <= last_chan:
            self.channels[irow].append(ichan)
            istrip = wire2strip(ichan, irow, first_chan)
            self.sensor_channels[strip_row].append(istrip)
            return True

        return False

    def get_n_unconnected(self) -> list:
        """Count number of unconnected channels.

        Return a list, one item per row.
        """
        nchan = [len(C) for C in self.channels]
        return nchan

    def get_max_consecutive_from_list(self, holes):
        """Return max widht of holes."""
        mx_width = []
        lst_holes = []
        for irow, row in enumerate(holes):
            if len(row) == 0:
                mxW = 0

            else:
                mxW = -1
                for h in row:
                    lst_holes.append(Hole(0, self.id, irow, h[0], h[1]))
                    mxW = max(mxW, h[1])

            mx_width.append(mxW)

        return mx_width, lst_holes


    def get_max_consecutive(self):
        """Returns the largest 'hole'."""
        mx_width, _ = self.get_max_consecutive_from_list(self.holes)
        return mx_width

    def get_max_sensor_consecutive(self):
        """Return largest hole in sensor."""
        mx_width, holes = self.get_max_consecutive_from_list(self.sensor_holes)
        return mx_width, holes

class SensorHoles:
    """Holes in sensor."""

    def __init__(self, param, win=None, sid=0):
        """Initialization.

        Args:
            param: sensor wirebon params
        """
        self.win = win
        self.id = sid
        self.param = param
        self.nchan = 0
        self.nhybrid = len(param)
        self.hybrids = []
        for i, P in enumerate(param):
            H = HybridHoles(P, hid=i, win=win)
            self.hybrids.append(H)
            self.nchan += H.nchan

    def ready(self):
        """Call when all channels are in."""
        for H in self.hybrids:
            H.ready()

    def get_n_hyb(self):
        """Return number of hybrids."""
        return len(self.hybrids)

    def get_hybrid(self, i):
        """Return i-th hybrid."""
        return self.hybrids[i]

    def get_max_consecutive(self):
        """Max number of consecutive unconnected channels.

        This is ordered by row.
        """
        mx_width = [0 for x in range(4)]
        for hyb in self.hybrids:
            mxW = hyb.get_max_consecutive()
            for j, val in enumerate(mxW):
                mx_width[j] = max(mx_width[j] , val)

        return mx_width

    def get_max_sensor_consecutive(self):
        """MAx widht of holes in sensor."""
        mx_width = -1
        holes = []
        for hyb in self.hybrids:
            mxW, hyb_holes = hyb.get_max_sensor_consecutive()
            for H in hyb_holes:
                H.sensor = self.id

            holes.extend(hyb_holes)
            for v in mxW:
                mx_width = max(mx_width, v)

        return mx_width, holes

    def get_n_unconnected(self):
        """Count number of unconnected channels.

        Return a list, one item per row.
        """
        nchan = [0, 0, 0, 0]
        for hyb in self.hybrids:
            nc = hyb.get_n_unconnected()
            for i, n in enumerate(nc):
                nchan[i] += n

        return nchan


class ModuleHoles:
    """Holes in Modules."""

    def __init__(self, param, win=None):
        """Initialization.

        Args:
            param: module wirebond params
        """
        self.win = win
        self.nsensor = len(param)
        self.nchan = 0
        self.sensors = []
        for i, P in enumerate(param):
            S = SensorHoles(P, sid=i, win=win)
            self.sensors.append(S)
            self.nchan += S.nchan

    def ready(self):
        """Call when all channels are in."""
        for S in self.sensors:
            S.ready()

    def get_max_consecutive(self):
        """Max number of consecutive unconnected channels.

        This is ordered by row.
        """
        mx_width = [-1, -1, -1, -1]
        for S in self.sensors:
            mxW = S.get_max_consecutive()
            for j in range(4):
                mx_width[j] = max(mx_width[j], mxW[j])

        return mx_width

    def get_max_sensor_consecutive(self):
        """The maximum number of consecutive channels per strip row."""
        mx_width = -1
        module_holes =  []
        for S in self.sensors:
            width, holes = S.get_max_sensor_consecutive()
            module_holes.extend(holes)
            mx_width = max(mx_width, width)

        return mx_width, module_holes


    def get_n_unconnected(self) -> list:
        """Count number of unconnected channels.

        Return a list, one item per row.
        """
        nchan = [0, 0, 0, 0]
        for S in self.sensors:
            nc = S.get_n_unconnected()
            for i, n in enumerate(nc):
                nchan[i] += n

        return nchan

    def get_total_unconnected(self) -> int:
        """Return total number of unconnected wires."""
        unc = self.get_n_unconnected()
        out = 0
        for v in unc:
            out += v

        return int(out)


def get_module_param(SN):
    """Get parameters of module type.

    Args:
        SN: Serial Number

    Returns:
        list: list with bond numbers.
    """
    if len(SN) != 14 or SN[:3]!="20U":
        raise ValueError("Wrong serial number {}".format(SN))

    if SN[3:5] != "SE":
        raise ValueError("Cannot handle barrel modules yet.")

    mod_type  = SN[5:7]
    if mod_type[0] != "M":
        raise ValueError("Does not seem to be a RingModule: {}".format(SN))

    ring = int(mod_type[-1])
    param = module_param[ring]

    return param


class WireBond(dbGtkUtils.ITkDBWindow):
    """Main window."""

    def __init__(self, session, title="", help_link=__HELP_LINK__):
        """Initialization."""
        super().__init__(title=title, session=session, help_link=help_link)
        self.pdb = None
        self.models = {}
        self.holes = {}
        self.institute = self.pdb_user["institutions"][0]["code"]
        self.inst_combo = None
        self.module_SN = None
        self.alternativeID = None
        self.combo = None
        self.tree = None
        self.lut = {}
        self.module_type = None
        self.init_window()

    def init_window(self):
        """Creates the GUI."""
        self.hb.props.title = "Wire Bond"

        # Button to upload
        button = Gtk.Button()
        icon = Gio.ThemedIcon(name="document-send-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        button.set_tooltip_text("Click to upload test")
        button.connect("clicked", self.upload_test)
        self.hb.pack_end(button)

        button = Gtk.Button()
        icon = Gio.ThemedIcon(name="document-save-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        button.set_tooltip_text("Click to save test file")
        button.connect("clicked", self.save_test)
        self.hb.pack_end(button)

        # Button to upload
        button = Gtk.Button()
        icon = Gio.ThemedIcon(name="document-open-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        button.set_tooltip_text("Click to read local data file.")
        button.connect("clicked", self.read_file)
        self.hb.pack_end(button)

        # Data panel
        grid = Gtk.Grid(column_spacing=5, row_spacing=1)

        # The shipment receiver
        institute = self.create_institute_combo(True)
        institute.connect("changed", self.on_institute)
        institute.set_tooltip_text("Select the Institute.")
        dbGtkUtils.set_combo_iter(institute, self.institute)

        lbl = Gtk.Label(label="Institute")
        lbl.set_xalign(0)
        grid.attach(lbl, 0, 0, 1, 1)
        grid.attach(institute, 1, 0, 1, 1)
        self.inst_combo = institute



        # The lookup table
        lbl = Gtk.Label(label="Lookup Table")
        lbl.set_xalign(0)
        grid.attach(lbl, 2, 0, 1, 1)

        self.testF = Gtk.FileChooserButton()
        self.testF.set_tooltip_text("Click to select Lookup table.")

        grid.attach(self.testF, 3, 0, 1, 1)
        self.testF.connect("file-set", self.on_lut)


        for i, tit in enumerate(["Operator", "Bond Machine", "Wire Batch", "SN", "Date"]):
            lbl = Gtk.Label(label=tit)
            lbl.set_xalign(0)
            grid.attach(lbl, 0, i+1, 1, 1)

        self.operator = dbGtkUtils.new_small_text_entry()
        self.machine = dbGtkUtils.new_small_text_entry()
        self.batch = dbGtkUtils.new_small_text_entry()
        #self.SN = dbGtkUtils.new_small_text_entry()

        self.SN = itkdb_gtk.dbGtkUtils.TextEntry(small=True)
        self.SN.connect("text-changed", self.on_SN_changed)


        self.date = dbGtkUtils.TextEntry(small=True)
        self.date.entry.set_text(ITkDButils.get_db_date())
        self.date.connect("text_changed", self.new_date)

        grid.attach(self.operator,      1, 1, 1, 1)
        grid.attach(self.machine,       1, 2, 1, 1)
        grid.attach(self.batch,         1, 3, 1, 1)
        grid.attach(self.SN.entry,      1, 4, 1, 1)
        grid.attach(self.date.widget,   1, 5, 1, 1)

        self.mainBox.pack_start(grid, True, True, 0)

        # Prepare combo and all the models
        lbl = Gtk.Label(label="Choose section.")
        lbl.set_xalign(0)
        self.mainBox.pack_start(lbl, True, True, 0)

        combo = self.create_combo()
        self.mainBox.pack_start(combo, True, True, 0)

        # The tree view
        scrolled = self.create_tree_view()
        self.mainBox.pack_start(scrolled, True, True, 5)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.mainBox.pack_start(box, False, False, 0)
        dbGtkUtils.add_button_to_container(box, "Add Bond",
                                           "Click to add a new bond or bond range.",
                                           self.add_item)

        dbGtkUtils.add_button_to_container(box, "Remove Bond",
                                           "Click to remove selected bond.",
                                           self.remove_item)

        #
        # The text view and buffer
        #
        self.mainBox.pack_start(self.message_panel.frame, True, True, 0)
        self.write_message("wirebond GUI\n")

    def on_lut(self, fdlg):
        """Get look-up table."""
        fnam = Path(fdlg.get_filename())
        if not fnam.exists():
            dbGtkUtils.complain("Cannot open Luukup Table.",
                                "File {} does not exist.".format(fnam))
            return

        lut = {}
        module_map = {}
        section = None
        i_local = 0
        i_std = 1
        indx = ["local", "standard"]
        found_format = False
        with open(fnam, 'r', encoding="UTF-8") as fin:
            for line in fin:
                line = line.strip()

                # Remove comments.
                ipos = line.find('#')
                jpos = line.find("#!")
                if jpos>=0 and ipos==jpos:
                    if found_format:
                        dbGtkUtils.complain("A second format line was found.",
                                            "Onely one is allowed. stopr map parsing.")
                        return

                    indx = [x.lower() for x in line[ipos+2:].split()]
                    try:
                        i_local = indx.index("local")
                        i_std = indx.index("standard")
                        found_format = True
                    except ValueError:
                        dbGtkUtils.complain("Wrong format desciption string.",
                                            "The words 'local' and 'standard' should be there.\n{}".format(line))
                        return

                    continue

                if ipos >= 0:
                    line = line[:ipos].strip()

                if len(line) == 0:
                    continue

                # Check for new section
                ipos = line.find(':')
                if ipos >= 0:
                    section = line[:ipos].strip().upper()
                    if section in module_map:
                        dbGtkUtils.complain("Section {} already in map.".format(section), "Stop parsing bond Lookup table.")
                        return

                    lut = {}
                    module_map[section] = lut
                    continue

                if section is None:
                    continue

                values = line.split()
                if len(values)!=len(indx):
                    dbGtkUtils.complain("Cannot read Lookup table.", "Wrong line format: {}".format(line))
                    return

                v_local = range_to_list(values[i_local])
                v_std = range_to_list(values[i_std])

                if len(v_local) != len(v_std):
                    dbGtkUtils.complain("Wrong Lookup table.",
                                        "Ranges have different length: {}".format(line))
                    return

                for L, S in zip(v_local, v_std):
                    lut[L] = S

        self.lut = module_map

    def convert_channel(self, C):
        """Convert channel according to LUT

        Args:
            C (str): channel number

        """
        try:
            return self.lut[self.module_type][C]

        except KeyError:
            return C

    def on_institute(self, combo):
        """Institute changed."""
        name = self.get_institute_from_combo(combo)
        if name:
            self.institute = name

    def on_SN_changed(self, entry, value):
        """New SN given. Ask in PDB,"""
        if len(value) <= 0:
            return

        obj = itkdb_gtk.ITkDButils.get_DB_component(self.session, value)
        if obj is not None and obj["serialNumber"] is not None:
            entry.set_text(obj["serialNumber"])
            alternativeID = obj["alternativeIdentifier"]
            module_SN = obj["serialNumber"]
            if len(module_SN) == 14 and module_SN.startswith("20USEM"):
                self.module_SN = module_SN
                self.alternativeID = alternativeID
                self.module_type = module_SN[5:7]

            else:
                itkdb_gtk.dbGtkUtils.complain("Invalid SN: {}".format(module_SN), "Not a Ring module")

        else:
            itkdb_gtk.dbGtkUtils.complain("Invalid SN", value)

    def on_name_combo_changed(self, combo):
        """Change model in TreeView."""
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            param = model[tree_iter][1]
            view_model = self.models[param]
            self.tree.set_model(view_model)
        else:
            self.write_message("Cannot find model for {}\n".format(param))

    def create_combo(self):
        """Create the combo."""
        model = Gtk.ListStore(str, str)
        for txt, param in test_parameters.items():
            model.append([txt, param])

            M = Gtk.ListStore(str, str)
            M.append(["", ""])
            self.models[param] = M

        self.combo = Gtk.ComboBox.new_with_model_and_entry(model)
        self.combo.set_entry_text_column(0)
        self.combo.set_active(0)
        self.combo.connect("changed", self.on_name_combo_changed)
        return self.combo

    def create_tree_view(self, size=150):
        """Creates the tree vew with the attachmens."""
        tree_iter = self.combo.get_active_iter()
        combo_model = self.combo.get_model()
        param = combo_model[tree_iter][1]
        model = self.models[param]

        self.tree = Gtk.TreeView(model=model)
        self.tree.connect("button-press-event", self.button_pressed)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.add(self.tree)
        scrolled.set_size_request(-1, size)

        renderer = Gtk.CellRendererText()
        renderer.set_property("editable", True)
        renderer.connect("edited", self.channel_edited)
        column = Gtk.TreeViewColumn("Channel", renderer, text=0)
        self.tree.append_column(column)

        renderer = Gtk.CellRendererText()
        renderer.set_property("editable", True)
        renderer.connect("edited", self.failure_edited)
        column = Gtk.TreeViewColumn("Failure", renderer, text=1)
        self.tree.append_column(column)

        return scrolled

    def text_edited(self, icol, path, text):
        """Text has been edited in the TreeView"""
        if len(text) == 0:
            return

        model = self.tree.get_model()

        n_child = model.iter_n_children()
        current_child = int(path)
        if n_child-current_child == 1:
            model.append(["", ""])

        model[path][icol] = text

    def channel_edited(self, widget, path, text):
        """Handles edition in channel number cell."""
        if not text.isnumeric():
            if valid_channel.match(text) is None:
                dbGtkUtils.complain("Wrong channel number", "Invalid channel number: {}".format(text))
                return

        self.text_edited(0, path, text)

    def failure_edited(self, widget, path, text):
        """Handles edition in comment."""
        self.text_edited(1, path, text)


    def new_date(self, entry, value):
        """new date given at input."""
        d = dbGtkUtils.parse_date_as_string(value)
        if d is not None:
            self.date.set_text(d)

    def button_pressed(self, tree, event):
        """Button pressed."""
         # double click shows attachments
        if event.button == 1 and event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS:
            #self.write_message("This is a double click.\n")
            return

        if event.button != 3:
            return

        # Create popup menu
        select = self.tree.get_selection()
        model, lv_iter = select.get_selected()
        values = None
        if lv_iter:
            values = model[lv_iter]

        else:
            P = tree.get_path_at_pos(event.x, event.y)
            if P:
                lv_iter = model.get_iter(P[0])
                values = model[lv_iter]

        if not values:
            return

        menu = Gtk.Menu()

        item_show = Gtk.MenuItem(label="Delete")
        item_show.connect("activate", self.on_delete_item, (model, lv_iter, values))
        menu.append(item_show)

        menu.show_all()
        menu.popup_at_pointer(event)

    def on_delete_item(self, item, data):
        """Delete bond in list view."""
        model, lv_iter, _ = data
        model.remove(lv_iter)

    def remove_item(self, *args):
        """REmoves selected bond."""
        select = self.tree.get_selection()
        model, lv_iter = select.get_selected()
        if lv_iter:
            model.remove(lv_iter)

    def add_item(self, *args):
        """Adds a new item in the current model."""
        out = dbGtkUtils.get_a_list_of_values("Add Item", ["Channel", "Comment"])
        if len(out) == 2:
            model = self.tree.get_model()
            model[-1] = out
            model.append(["", ""])

    def quit(self, *args):
        """Quits the application."""
        if self.pdb:
            self.pdb.die()

        self.hide()
        self.destroy()

    def compute_repaired(self, skeleton):
        """Compute number of repaired."""
        nrepaired = 0
        for key, values in skeleton["results"].items():
            if key.find("REPAIRED")<0 or key.find("ROW")<0:
                continue

            nrepaired += len(values)

        if nrepaired>0:
            skeleton["problems"] = True
            skeleton["comments"].append("Number of repaired FE bonds: {}".format(nrepaired))

        return nrepaired

    def compute_hybrid_to_pb(self, skeleton):
        """Compute number of failures and repairs."""
        n = count_items(skeleton["results"]["REPAIRED_HYBRID_TO_PB"])
        n = count_items(skeleton["results"]["FAILED_HYBRID_TO_PB"])
        if n:
            msg = "Hybrid to PB: {} failing bonds.".format(n)
            skeleton["comments"].append(msg)
            skeleton["passed"] = False
            self.write_message("{}\n".format(msg))
            for key in skeleton["results"]["FAILED_HYBRID_TO_PB"]:
                defect = {
                    "description": "Unbonded: Hybrid to PB",
                    "name": "UNBODED",
                    "properties": {
                        "wire_number": range_to_list(key)
                    }
                }
                skeleton["defects"].append(defect)


    def compute_module_to_frame(self, skeleton):
        """Compute number of failures and repairs."""
        n = count_items(skeleton["results"]["REPAIRED_MODULE_TO_FRAME"])
        n = count_items(skeleton["results"]["FAILED_MODULE_TO_FRAME"])
        if n:
            msg = "Module to test frame: {} failing bonds.".format(n)
            skeleton["comments"].append(msg)
            skeleton["passed"] = False
            self.write_message("{}\n".format(msg))
            for key in skeleton["results"]["FAILED_MODULE_TO_FRAME"]:
                defect = {
                    "description": "Unbonded: Module to Frame",
                    "name": "UNBODED",
                    "properties": {
                        "wire_number": range_to_list(key)
                    }
                }
                skeleton["defects"].append(defect)

    def compute_unconnected(self, results):
        """Compute number of unconnected."""
        try:
            param = get_module_param(self.SN.get_text())
        except ValueError as E:
            dbGtkUtils.complain("Wrong SN number", str(E))
            return None

        M = ModuleHoles(param=param, win=self)

        defects = []
        for test, values in results.items():
            if test.find("FAILED") < 0:
                continue
            if test.find("ROW") < 0:
                continue

            irow = int(test[-1]) - 1

            # Get list of all channels with wirebond notation.
            out = [int(x) for x in values.keys()]
            # Translate to sensor, hybrids, etc.
            for S in M.sensors:
                for H in S.hybrids:
                    H.add_channel(irow, out)
                    H.holes[irow] = find_holes(H.channels[irow])

            # add defects
            defects.append(
                {
                    "description": "Unbonded Channel",
                    "name": "UNBONDED",
                    "properties": {
                        "front_end_row": irow,
                        "wire_number": out
                    }
                }
            )

        # Now get sensor strips.
        M.ready()
        unconnected = M.get_n_unconnected()
        mx_consecutive = M.get_max_consecutive()
        mx_sensor_width, module_holes = M.get_max_sensor_consecutive()

        out = {}
        out["comments"] = []
        out["defects"] = defects
        for irow in range(4):
            key = "MAX_CONT_UNCON_ROW{}".format(irow+1)
            out[key] = mx_consecutive[irow]

        self.write_message("Found {} clusters of unconnected strips in sensor.\n".format(len(module_holes)))
        for H in module_holes:
            self.write_message("{}\n".format(H))

        if mx_sensor_width > 0:
            self.write_message("Max width of consecutive unconnected strips: {}\n". format(mx_sensor_width))

        out["MAX_UNCON_SENSOR_CHAN"] = mx_sensor_width
        if mx_sensor_width > 8:
            out["passed"] = False
            out["comments"].append("Too many consecutive sensor strips unconnected: {}".format(mx_sensor_width))

        nstrips = 0
        for v in unconnected:
            nstrips += v

        percent = 100*nstrips/M.nchan
        out["TOTAL_PERC_UNCON_SENSOR_CHAN"] = percent
        if out["TOTAL_PERC_UNCON_SENSOR_CHAN"] > 1.0:
            out["passed"] = False
            out["comments"].append("More than 1%% of channels unconnected: {:.1f}%%".format(percent))

        return out

    def get_unconnected(self, skeleton):
        """Fill the test DTO with unconnected information."""
        out = self.compute_unconnected(skeleton["results"])
        if out is None:
            raise ValueError("Wrong SN")

        for key, val in out.items():
            if key in ["passed", "problems"]:
                skeleton[key] = out[key]
                continue

            if key == "comments":
                for C in out[key]:
                    skeleton[key].append(C)

                continue

            if key == "defects":
                for D in out[key]:
                    skeleton[key].append(D)

                continue


            skeleton["results"][key] = val

    def read_file(self, *args):
        """Read local data file."""
        dialog = Gtk.FileChooserDialog(
            title="Please choose a file",
            parent=self,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,
            Gtk.ResponseType.OK,
        )
        filter_text = Gtk.FileFilter()
        filter_text.set_name("JSON files")
        filter_text.add_mime_type("application/json")
        dialog.add_filter(filter_text)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            ofile = dialog.get_filename()
            self.write_message("Loading data from {}\n".format(ofile))
            with open(ofile, 'r', encoding="utf-8") as data_file:
                data = json.load(data_file)
                self.parse(data)

        dialog.hide()
        dialog.destroy()

    def parse(self, data):
        """Parses a JSon dictionary."""
        try:
            dbGtkUtils.set_combo_iter(self.inst_combo, data["institution"])
        except KeyError:
            self.write_message("institution value is not in the loaded file\n.")

        self.operator.set_text(data["properties"]["OPERATOR"])
        self.machine.set_text(data["properties"]["BOND_MACHINE"])
        self.batch.set_text(data["properties"]["BONDWIRE_BATCH"])
        self.SN.set_text(data["component"])
        self.date.set_text(data["date"])
        for key, val in data["results"].items():
            model = self.models[key]
            model.clear()
            for chan, msg in val.items():
                model.append([chan, msg])

            model.append(["", ""])

    def get_list_of_channels(self, data):
        """Creates the lists of channels."""
        for key, model in self.models.items():
            lv_iter = model.get_iter_first()
            out = {}
            while lv_iter:
                chan, comm = model[lv_iter]
                if len(chan) > 0:
                    out[chan] = comm

                lv_iter = model.iter_next(lv_iter)

            data["results"][key] = out

    def fix_list_of_channels(self, data):
        """Expand ranges and, eventually, apply LUT.

        Args:
            data: The test payload.
        """
        for tit, section in data["results"].items():
            if not isinstance(section, dict):
                continue

            range_items = []
            added_items = []
            for key, comment in section.items():
                values = list(map(str.strip, key.split(',')))
                if ',' in key or '-' in key:
                    range_items.append(key)

                else:
                    continue

                for V in values:
                    for i in range_to_list(V):
                        added_items.append((str(i), comment))

            for key in range_items:
                section.pop(key)

            for key, comm in added_items:
                section[key] = comm

            if len(self.lut)>0 and len(section)>0:
                tmp = copy.deepcopy(section)
                section.clear()
                for key, val in tmp.items():
                    section[self.convert_channel(key)] = val


    def save_test(self, *args):
        """Save Test file."""
        dialog = Gtk.FileChooserDialog(
            title="Please choose a file", parent=self, action=Gtk.FileChooserAction.SAVE
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,
            Gtk.ResponseType.OK,
        )
        filter_text = Gtk.FileFilter()
        filter_text.set_name("JSON files")
        filter_text.add_mime_type("application/json")
        dialog.add_filter(filter_text)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            ofile = dialog.get_filename()
            data = self.get_test_data()
            with open(ofile, 'w', encoding="UTF-8") as of:
                json.dump(data, of, indent=3)

        dialog.hide()
        dialog.destroy()

    def get_test_data(self):
        """Get the test data."""
        data = {
            "institution": self.institute,
            "date": ITkDButils.get_db_date(),
            "runNumber": "1",
            "properties": {},
            "results": {},
            "comments": [],
            "defects": []
        }
        self.get_test_header(data)
        self.get_list_of_channels(data)
        return data

    def get_test_header(self, data):
        """Get Basic test data."""
        SN = self.SN.get_text()
        operator = self.operator.get_text()
        machine = self.machine.get_text()
        batch = self.batch.get_text()

        if not SN or len(SN)==0:
            SN = dbGtkUtils.get_a_value("Module Serial Number",
                                        "Module serial Number is missing")

        if len(operator) == 0 or len(machine) == 0:
            values = dbGtkUtils.get_a_list_of_values(
                "Missing Values",
                ["SN", "Operator", "Wire Bonder"],
                defaults=[SN, operator, machine],
            )
            if len(values) == 4:
                SN, operator, machine = values
            else:
                self.write_message("Something went wrong while requesting missing information.\n")

        data["component"] = SN
        data["properties"]["OPERATOR"] = operator
        data["properties"]["BOND_MACHINE"] = machine
        data["properties"]["BONDWIRE_BATCH"] = batch
        data["institution"] = self.institute
        if data["runNumber"] == "-1":
            data["runNumber"] = "1"

        data["date"] = self.date.get_text()



    def upload_test(self, *args):
        """Upload test."""
        if self.session is None:
            self.pdb = ITkDBlogin.ITkDBlogin()
            client = self.pdb.get_client()
            if client is None:
                dbGtkUtils.complain("Could not connect to DB with provided credentials.")
                self.pdb.die()

            else:
                self.session = client

        defaults = {
            "institution": self.institute,
            "runNumber": "1",
            "date":  ITkDButils.get_db_date()
        }
        skeleton = ITkDButils.get_test_skeleton(self.session, "MODULE", "MODULE_WIRE_BONDING", defaults)

        self.get_test_header(skeleton)
        self.get_list_of_channels(skeleton)
        self.fix_list_of_channels(skeleton)
        try:
            self.get_unconnected(skeleton)
            self.compute_repaired(skeleton)
            self.compute_hybrid_to_pb(skeleton)
            self.compute_module_to_frame(skeleton)

        except ValueError:
            return

        uploadW = UploadTest.UploadTest(self.session, payload=skeleton)
        # uploadW.run()


def main():
    """Main entry."""
    dlg = ITkDBlogin.ITkDBlogin()
    client = dlg.get_client()
    if client is None:
        print("Could not connect to DB with provided credentials.")
        dlg.die()
        sys.exit()

    client.user_gui = dlg


    win = WireBond(client, title="WireBond")
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    try:
        Gtk.main()

    except KeyboardInterrupt:
        print("Arrrgggg!!!")

    dlg.die()

if __name__ == "__main__":
    main()
