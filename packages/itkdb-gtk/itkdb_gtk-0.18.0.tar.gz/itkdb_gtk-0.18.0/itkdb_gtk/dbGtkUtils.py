"""A set of GTK utilities for DB scripts."""
import sys
import json
import time
import pathlib

from collections.abc import Iterable
from copy import deepcopy
from datetime import datetime
import webbrowser

import dateutil.parser
import numpy as np


import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GObject, Gio, GLib


try:
    import itkdb_gtk

except ImportError:
    cwd = pathlib.Path(__file__).parent.parent
    sys.path.append(cwd.as_posix())

from itkdb_gtk import ITkDButils


def parse_date(txt):
    """Parse a date."""
    try:
        return dateutil.parser.parse(txt, fuzzy=False)

    except dateutil.parser.ParserError:
        return None


def parse_date_as_string(txt):
    """Parse data and return DB compatible string."""
    D = parse_date(txt)
    if D is None:
        return D

    out = D.isoformat(timespec='milliseconds')
    if out[-1] not in ['zZ']:
        out += 'Z'

    return out

def is_a_date(txt):
    """check tha the input string is a date."""
    try:
        tl = txt.lower()
        if len(txt)<5 and (tl!="now" and tl!="today"):
            return False

        dateutil.parser.parse(txt, fuzzy=False)
        return True

    except (dateutil.parser.ParserError, OverflowError):
        return False

def new_small_text_entry():
    """Returs a new, smaller Gtk.Entry."""
    entry = Gtk.Entry()
    provider = Gtk.CssProvider()
    style_context = entry.get_style_context()
    font_size = 2.25*style_context.get_property("font-size", 0)
    css = "entry {{ min-height: {}px; }}".format(font_size)
    provider.load_from_data(css.encode())
    style_context.add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_SETTINGS)
    return entry

def set_entry_style(container):
    """Set max entry."""
    provider = Gtk.CssProvider()
    style_context = container.get_style_context()
    font_size = 2.25*style_context.get_property("font-size", 0)
    css = "{} {{ min-height: {}px; }}".format(container.get_name(), font_size)
    provider.load_from_data(css.encode())
    style_context.add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_SETTINGS)
    return container

def set_button_color(btn, bg_color, fg_color="white"):
    """Set button color"""
    css = "#{} {{background-image: none; background-color: {}; color: {}}}".format(btn.get_name(), bg_color, fg_color)
    provider = Gtk.CssProvider()
    provider.load_from_data(css.encode())
    style_context = btn.get_style_context()
    style_context.add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

def set_combo_iter(combo, txt, col=0):
    """Set scombo active iter to that containing txt in column col."""
    model = combo.get_model()
    lv_iter = model.get_iter_first()
    while lv_iter:
        val = model.get_value(lv_iter, col)
        if val == txt:
            combo.set_active_iter(lv_iter)
            break

        lv_iter = model.iter_next(lv_iter)


def is_iterable(obj):
    """Tell if an object is iterable. Strings are not considered iterables."""
    if isinstance(obj, Iterable):
        if isinstance(obj, str) or isinstance(obj, bytes):
            return False
        else:
            return True
    else:
        return False


class MyEncoder(json.JSONEncoder):
    """To truncate the number of decimals in floats."""

    def default(self, o):
        """Format floats or deletate to JSonEncoder."""
        if isinstance(o, datetime):
            text = o.astimezone().isoformat()
            return text
        elif isinstance(o, np.integer):
            return int(o)
        elif isinstance(o, np.floating):
            return float(o)
        elif isinstance(o, np.ndarray):
            return o.tolist()
        else:
            return super().default(o)


def empty_container(container):
    """Remove all children from a container.

    Args:
        container: The container.

    """
    chilren = [C for C in container.get_children()]
    for C in chilren:
        container.remove(C)


def replace_in_container(container, child):
    """Replace a child from a single-child container.

    Args:
        container: the container
        child: the new child to be added

    """
    empty_container(container)
    if isinstance(container, Gtk.Box):
        container.pack_end(child, True, True, 0)
    else:
        container.add(child)
    container.show_all()


def complain(main_title, second_text="", parent=None):
    """Open an error dialog.

    Args:
        main_title: Main text in window
        second_text: Second text
        parent: dialog parent

    """
    dialog = Gtk.MessageDialog(
        transient_for=parent,
        flags=0,
        message_type=Gtk.MessageType.ERROR,
        buttons=Gtk.ButtonsType.OK,
        text=main_title,
    )
    dialog.format_secondary_text(second_text)
    dialog.run()
    dialog.destroy()


def ask_for_confirmation(main_title, second_text, parent=None):
    """Ask for action cofirmation.

    Args:
        main_title: Main title in the message window
        second_text: Secondary text in the message widow
        parent (optional): The parent window. Defaults to None.

    Return:
        OK: True if OK button clicked.

    """
    dialog = Gtk.MessageDialog(
        transient_for=parent,
        flags=0,
        message_type=Gtk.MessageType.INFO,
        text=main_title
    )
    dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK)
    dialog.format_secondary_text(second_text)
    out = dialog.run()
    dialog.destroy()
    return (out == Gtk.ResponseType.OK)

class TextEntry(GObject.GObject):
    """Create a Gtk text entry/view object."""
    __gsignals__ = {
        "text_changed": (GObject.SIGNAL_RUN_FIRST, None, (str,))
    }

    def __init__(self, n_lines=1, small=False):
        """Init."""
        GObject.GObject.__init__(self)
        self.tmp_txt = ""
        self.nlines = n_lines
        self.do_emit = True
        if self.nlines > 1:
            self.widget = Gtk.Frame()
            scrolled = Gtk.ScrolledWindow()
            scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
            scrolled.set_hexpand(True)
            scrolled.set_vexpand(True)

            self.widget.add(scrolled)
            self.entry = Gtk.TextView()
            scrolled.add(self.entry)

        else:
            if small:
                self.widget = new_small_text_entry()
            else:
                self.widget = Gtk.Entry()

            self.widget.connect("focus-in-event", self.on_enter)
            self.widget.connect("focus-out-event", self.on_leave)
            self.entry = self.widget

    def do_my_signal(self, *args):
        """Signal handler."""
        return

    def on_enter(self, *args):
        """On enter."""
        self.tmp_txt = self.widget.get_text().strip()
        return False

    def on_leave(self, *args):
        """On leave."""
        val = self.widget.get_text().strip()
        if val != self.tmp_txt:
            self.do_emit = False
            self.emit("text_changed", val)
            self.do_emit = True

    def get_text(self):
        """Return the text."""
        if self.nlines > 1:
            buff = self.entry.get_buffer()
            start = buff.get_start_iter()
            end = buff.get_end_iter()
            return buff.get_text(start, end, False)

        else:
            return self.entry.get_text()

    def set_text(self, text):
        """Sets text."""
        if text is None:
            return

        if self.nlines > 1:
            self.entry.get_buffer().set_text(text)
        else:
            self.entry.set_text(text)
            if self.do_emit:
                self.do_emit = False
                self.emit("text_changed", text)
                self.do_emit = True

def get_a_value(main_title, second_text=None, is_tv=False, parent=None):
    """Open a dialog to get a value.

    Args:
        main_title: Main title in the message window
        is_tv: If true show a text view rathar than an entry.
        second_text: Secondary text in the message widow
        parent (optional): The parent window. Defaults to None.

    Return:
        value: The value in the entry

    """
    dlg = Gtk.Dialog(title="Get a Value",
                     transient_for=parent,
                     flags=0)
    dlg.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                    Gtk.STOCK_OK, Gtk.ResponseType.OK)
    area = dlg.get_content_area()
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    area.add(box)

    box.pack_start(Gtk.Label(label=main_title), False, True, 0)
    if second_text and len(second_text):
        box.pack_start(Gtk.Label(label=second_text), False, True, 0)

    entry = TextEntry(3 if is_tv else -1)

    box.pack_start(entry.widget, False, True, 0)
    dlg.show_all()

    rc = dlg.run()
    if rc == Gtk.ResponseType.OK:
        out = entry.get_text().rstrip()
    else:
        out = None

    dlg.hide()
    dlg.destroy()

    return out


def get_a_list_of_values(main_title, labels, defaults=None, second_text=None, parent=None):
    """Get a list of values.

    Args:
        main_title: Main title for window
        labels: List of labes to get the values. If the label ends with /v
                then a TextView will be shown instead of a TextEntry.
        defaults (optional): default values-
        second_text (optional): Second title for window-. Defaults to None.

    Returns:
        list with values

    """
    dlg = Gtk.Dialog(title="Get List of values",
                     transient_for=parent,
                     flags=0)

    dlg.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                    Gtk.STOCK_OK, Gtk.ResponseType.OK)
    area = dlg.get_content_area()
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    area.pack_start(box, False, True, 2)

    lbl = Gtk.Label()
    lbl.set_markup("<b>{}</b>".format(main_title))
    box.pack_start(lbl, False, True, 5)
    if second_text and len(second_text):
        box.pack_start(Gtk.Label(label=second_text), False, True, 0)

    entries = []
    values = []
    is_text_view = []
    vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    area.pack_start(vbox, False, True, 0)
    for i, txt in enumerate(labels):
        use_tv = False
        if txt.endswith("/v"):
            is_text_view.append(True)
            use_tv = True
            txt = txt[:-2]
        else:
            is_text_view.append(False)

        lbl = Gtk.Label(label=txt)
        lbl.set_justify(Gtk.Justification.LEFT)
        vbox.pack_start(lbl, False, False, 0)

        entry = TextEntry(3 if use_tv else -1)
        try:
            entry.set_text(defaults[i])

        except (TypeError, IndexError):
            pass

        vbox.pack_start(entry.widget, False, False, 0)
        entries.append(entry)

    dlg.show_all()
    rc = dlg.run()
    if rc == Gtk.ResponseType.OK:
        for entry, is_tv in zip(entries, is_text_view):
            values.append(entry.get_text())

    dlg.hide()
    dlg.destroy()
    return values


def add_button_to_container(box, label, tooltip=None, callback=None):
    """Creates a buttons and adds to container.

    Args:
        box: The container.
        label: The button label
        tooltip (optional): Tooltip message. Defaults to None.
        callback (optional): callback function. Defaults to None.

    """
    btn = Gtk.Button(label=label)

    if tooltip:
        btn.set_tooltip_text(tooltip)

    if callback:
        btn.connect("clicked", callback)

    box.pack_start(btn, True, False, 0)

    return btn


class MessagePanel(object):
    """Encapsulates a TExtView object to show messages."""

    def __init__(self, size=100):
        """Initializarion."""
        self.frame = None
        self.text_view = Gtk.TextView()
        self.textbuffer = self.text_view.get_buffer()

        self.__create_message_panel(size)


    def __create_message_panel(self, size):
        """Creates a message panel within a frame.

        Args:
            size: size of the panel

        Returns:
            Gtk.TextBuffer, Gtk.Frame
        """
        frame = Gtk.Frame()
        frame.set_shadow_type(Gtk.ShadowType.IN)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.set_size_request(-1, size)
        frame.add(box)

        # The title for the tet view
        box.pack_start(Gtk.Label(label="Messages"), False, True, 0)

        # A scroll window with the text view
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.add(self.text_view)
        box.pack_start(scrolled, True, True, 0)
        self.frame = frame

    def scroll_to_end(self):
        """Scrolls text view to end."""
        end = self.textbuffer.get_end_iter()
        self.text_view.scroll_to_iter(end, 0, False, 0, 0)

    def write_message(self, text, write_date=True):
        """Writes text to Text Viewer."""
        nlines = self.textbuffer.get_line_count()
        if nlines > 100:
            start = self.textbuffer.get_iter_at_line(0)
            end = self.textbuffer.get_iter_at_line(75)
            self.textbuffer.delete(start, end)

        end = self.textbuffer.get_end_iter()
        if write_date:
            msg = "[{}]  {}".format(time.strftime("%d/%m/%y %T"), text)
        else:
            msg = text

        self.textbuffer.insert(end, msg)
        GLib.idle_add(self.scroll_to_end)

    def write(self, txt):
        """A write method."""
        self.write_message(txt, write_date=False)


class ITkDBWindow(Gtk.Window):
    """Base class for GUI main windows."""

    def __init__(self, title="", session=None, show_search=None, help_link=None, gtk_runs=True, panel_size=100):
        """Initialization.

        Args:
            title: The title of the window.
            session: ITkDB session.
            show_search: tooltip for search button in header (calls to query_db).
                         No search button if this is None.
            gtk_runs: If False, Gtk could not be loaded and app should be
                      terminal only.

        """
        self.session = session
        self.inst2code = {}
        self.code2inst = {}
        self.message_panel = None
        self.help = help_link
        self.pdb_user = ITkDButils.get_db_user(self.session)

        if gtk_runs:
            super().__init__(title=title)
            self.prepare_window(title, show_search, panel_size)

    def prepare_window(self, title, show_search, panel_size):
        """Inititalizes GUI."""
        # Prepare HeaderBar
        self.hb = Gtk.HeaderBar()
        self.hb.set_show_close_button(True)
        self.set_titlebar(self.hb)

        self.userLabel = Gtk.Button.new_with_label(self.session.user.name)
        self.userLabel.set_tooltip_text("Click to change user.")
        if hasattr(self.session, "user_gui"):
            self.session.user_gui.connect("new_login", self.new_login)
        self.userLabel.connect("clicked", self.reconnect)
        self.hb.pack_start(self.userLabel)

        if show_search:
            button = Gtk.Button()
            icon = Gio.ThemedIcon(name="system-search-symbolic")
            image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
            button.add(image)
            button.set_tooltip_text(show_search)
            button.connect("clicked", self.query_db)
            self.hb.pack_end(button)

        if self.help:
            button = Gtk.Button()
            icon = Gio.ThemedIcon(name="help-browser-symbolic")
            image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
            button.add(image)
            button.connect("clicked", self.show_help)
            self.hb.pack_end(button)


        # Create main content box
        self.mainBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.mainBox.set_property("margin-left", 6)
        self.mainBox.set_property("margin-right", 6)

        self.title_label = None
        if len(title)>0:
            lbl = Gtk.Label()
            lbl.set_markup("<big><b>{}\n</b></big>".format(title))
            lbl.set_xalign(0.5)
            self.mainBox.pack_start(lbl, False, False, 2)
            self.title_label = lbl

        self.add(self.mainBox)

        # The text view and buffer
        self.message_panel = MessagePanel(size=panel_size)

        # The button box
        btnBox = Gtk.ButtonBox(orientation=Gtk.Orientation.HORIZONTAL)

        btn = Gtk.Button(label="Quit")
        btn.connect("clicked", self.quit)
        btnBox.add(btn)

        self.mainBox.pack_end(btnBox, False, True, 0)

    def set_window_title(self, title):
        """Set window title."""
        hb = self.get_titlebar()
        hb.props.title = title
        if self.title_label:
            self.title_label.set_markup("<big><b>{}\n</b></big>".format(title))

    def quit(self, *args):
        """Quits the application."""
        self.hide()
        self.destroy()

    def show_help(self, *args):
        """Show help"""
        webbrowser.open(self.help)

    def query_db(self, *args):
        """Search button clicked."""
        return

    def new_login(self, obj, msg):
        """A new user logged in."""
        if msg == "<OK>":
            if hasattr(self.session, "user_gui"):
                self.session = self.session.user_gui.get_client()

            if self.userLabel.get_child():
                self.userLabel.get_child().set_text(self.session.user.name)

        else:
            self.write_message("Could not login.\n{}".format(msg))

    def reconnect(self, *args):
        """Reconnects."""
        if hasattr(self.session, "user_gui"):
            self.session.user_gui.reconnect(force=True)

    def create_institute_combo(self, only_user=False):
        """Create a combe with all institutes.
        
        Args:
            only_user: if True, add only institutes the user belongs to.
            
        """
        compltn = self.get_institute_list(only_user)
        combo = Gtk.ComboBox.new_with_model_and_entry(compltn.get_model())
        combo.set_entry_text_column(0)
        combo.get_child().set_completion(compltn)

        return combo

    def get_institute_list(self, only_user=False):
        """Get the institute list.
        
        Args:
            only_user: if True, add only institutes the user belongs to.
        
        """
        if only_user and self.pdb_user:
            sites = self.pdb_user["institutions"]
        else:
            sites = self.session.get("listInstitutions", json={})
            
        liststore = Gtk.ListStore(str, str)
        for site in sites:
            self.code2inst[site['code']] = site['name']
            self.inst2code[site['name']] = site['code']
            liststore.append([site["code"], site["code"]])
            liststore.append([site["name"], site["code"]])

        completion = Gtk.EntryCompletion()
        completion.set_model(liststore)
        completion.set_text_column(0)
        return completion

    def get_institute_from_combo(self, combo):
        """Get Institute from combo."""
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            name = model[tree_iter][1]

        else:
            name = combo.get_child().get_text()
            if name in self.inst2code:
                name = self.inst2code[name]

            elif name not in self.code2inst:
                name = None

        return name

    def create_text_view(self, size=50):
        """Create a frame wit hteh text view."""
        frame = Gtk.Frame()
        frame.set_shadow_type(Gtk.ShadowType.IN)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.set_size_request(-1, size)
        frame.add(box)

        # The title for the tet view
        box.pack_start(Gtk.Label(label="Messages"), False, True, 0)

        # A scroll window with the text view
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.add(self.text_view)
        box.pack_start(scrolled, True, True, 0)

        return frame

    def write_message(self, text):
        """Writes text to Text Viewer."""
        self.message_panel.write_message(text)


class DictDialog(Gtk.Grid):
    """Creates a dialog to show and edit variables in a JSon dict."""

    def __init__(self, values, hidden_keys=None):
        """Create the Gtk.Grid.

        Args:
            values: A dict (JSon-like)
            hidden_keys: keys tha twill not be shown.

        """
        super().__init__(column_spacing=5, row_spacing=1)

        self.set_border_width(10)
        self.factory = deepcopy(values)
        self.values = deepcopy(values)
        self.keys = {}
        self.containers = {}
        self.hidden_keys = hidden_keys if hidden_keys else {}
        self.show_values()

    def factory_reset(self):
        """Set values to original values."""
        self.values = deepcopy(self.factory)
        self.refresh()

    def on_enter(self, entry, *args):
        """Get the value when we first enter into the Entry."""
        self.keys[args[2]] = entry.get_text()

    def on_leave(self, entry, event, value, name):
        """Check, when leaving the entry, if the value has changed."""
        def str2bool(v):
            return v.lower() in ("yes", "true", "t", "1")

        val = self.keys[name]
        txt = entry.get_text()
        if val != txt:
            keys = name.split('.')
            itm = self.values
            for k in keys[:-1]:
                itm = itm[k]

            last_key = keys[-1]
            if isinstance(itm, tuple) or isinstance(itm, list):
                indx = int(last_key)
                tp = type(itm[indx])
                itm[indx] = tp(txt)

            elif isinstance(itm[last_key], bool):
                itm[last_key] = str2bool(txt)

            elif isinstance(itm[last_key], datetime):
                itm[last_key] = dateutil.parser.parse(txt)

            elif is_a_date(itm[last_key]):
                D = dateutil.parser.parse(txt)
                out = D.isoformat(timespec='milliseconds')
                if out[-1] not in ['zZ']:
                    out += 'Z'

                itm[last_key] = out
                self.containers[name].set_text(out)

            else:
                if itm[last_key] is None:
                    itm[last_key] = txt
                else:
                    tp = type(itm[last_key])
                    itm[last_key] = tp(txt)

    def show_item(self, value, name=None):
        """Handle a single item."""
        if isinstance(value, list) or isinstance(value, tuple):
            container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            for i, v in enumerate(value):
                key_name = "{}.{}".format(name, i)
                container.pack_start(self.show_item(v, key_name), True, True, 0)

        elif isinstance(value, dict):
            container = Gtk.Grid(column_spacing=5, row_spacing=0)
            irow = 0
            for key, val in value.items():
                if name:
                    key_name = "{}.{}".format(name, key)
                lbl = Gtk.Label(label=key)
                lbl.set_xalign(0.0)
                if is_iterable(val):
                    lbl.set_yalign(0.0)
                else:
                    lbl.set_yalign(0.5)

                container.attach(lbl, 0, irow, 1, 1)
                container.attach(self.show_item(val, key_name), 1, irow, 1, 1)
                irow = irow + 1

        else:
            if value is None:
                value = ""

            container = Gtk.Entry(text=value)
            provider = Gtk.CssProvider()
            style_context = container.get_style_context()
            font_size = 2.25*style_context.get_property("font-size", 0)
            css = "entry {{ min-height: {}px; }}".format(font_size)
            provider.load_from_data(css.encode())
            style_context.add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_SETTINGS)
            container.connect("populate-popup", self.add_insert_path)

            if name:
                container.set_name(name)
                self.containers[name] = container

            container.connect("focus-in-event", self.on_enter, value, name)
            container.connect("focus-out-event", self.on_leave, value, name)

        return container

    def add_insert_path(self, entry, menu, *args):
        """Adds a new item in the pop-up menu."""
        item = Gtk.MenuItem(label="Get file path")
        item.connect("activate", self.on_set_path, entry)
        menu.append(item)
        menu.show_all()

    def on_set_path(self, menu_item, entry):
        """Sets the path to the entry."""
        fdlg = Gtk.FileChooserNative(action=Gtk.FileChooserAction.OPEN, accept_label="Select")
        response = fdlg.run()
        if response == Gtk.ResponseType.ACCEPT:
            ifiles = [ipath for ipath in fdlg.get_filenames()]
            if len(ifiles)<1:
                return
            if len(ifiles) > 1:
                complain("More than one file selected","Choosing first.")

            fnam = ifiles[0]
            entry.set_text(fnam)
            self.on_leave(entry, None, None, entry.get_name())

    def set_value(self, key, value):
        """Set value of a container and key."""
        try:
            self.containers[key].set_text("{}".format(value))
            self.keys[key] = value
        except KeyError:
            complain("Key {} does not exist in DictDialog".format(key))

    def show_values(self):
        """Show the keys and values of a dictionary (JSON).

        Args:
            values: The dictionary object

        """
        irow = 0
        self.set_row_spacing(5)
        for key, value in self.values.items():
            if key in self.hidden_keys:
                continue

            lbl_key = Gtk.Label(label=key)
            lbl_key.set_xalign(0.0)
            if is_iterable(value):
                lbl_key.set_yalign(0.0)
            else:
                lbl_key.set_yalign(0.5)

            container = self.show_item(value, key)

            self.attach(lbl_key, 0, irow, 1, 1)
            self.attach(container, 1, irow, 1, 1)
            irow = irow + 1

    def refresh(self):
        """Refresh all values."""
        empty_container(self)
        self.show_values()
        self.show_all()
        self.queue_draw()

    @staticmethod
    def create_json_data_editor(data):
        """Create a dialog to show the JSon file."""
        dlg = Gtk.Dialog(title="Test Data")
        dlg.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                        Gtk.STOCK_OK, Gtk.ResponseType.OK)

        dlg.set_property("height-request", 500)
        box = dlg.get_content_area()
        value = DictDialog(data)
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.add(value)
        box.pack_start(scrolled, True, True, 10)

        dlg.show_all()
        rc = dlg.run()
        dlg.hide()
        dlg.destroy()

        return value.values, rc


def create_scrolled_dictdialog(the_dict, hidden=("component", "testType")):
    """Create a DictDialog within a scrolled window.

    Args:
        the_dict: the input dictionary with values.

    Returns:
        scrolled: the scrolled window
        gM: the DictDialog

    """
    gM = DictDialog(the_dict, hidden)
    scrolled = Gtk.ScrolledWindow()
    scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
    scrolled.add(gM)
    return scrolled, gM


def main():
    """Main entry."""
    result = {
        "component": "the_serial_nukber",
        "testType": "METROLOGY_AVS",
        "institution": "...",
        "runNumber": "...",
        "date": datetime.now(),
        "passed": True,
        "problems": False,
        "properties": {
            "OPERATOR": "operator"
        },
        "results": {
            "LOCATOR1_DIAMETER": True,
            "LOCATOR1_X": -1,
            "LOCATOR1_Y": -1,
            "LOCATOR2_DIAMETER": True,
            "LOCATOR2_X": -1,
            "LOCATOR2_Y": -1,
            "LOCATOR3_DIAMETER": -1,
            "FIDUCIAL1_DIAMETER": -1,
            "FIDUCIAL1_X": -1,
            "FIDUCIAL1_Y": -1,
            "FIDUCIAL2_X": -1,
            "FIDUCIAL2_Y": -1,
            "FIDUCIAL2_DIAMETER": -1,
            "COPLANARITY_FRONT": -1,
            "PARALLELISM_FRONT": -1,
            "COPLANARITY_BACK": -1,
            "PARALLELISM_BACK": -1,
            "ANGLE_VCHANNEL": -1,
            "ENVELOPE": -1,
            "FLAT_LOCAL_BACK": [
                543.0948648254819,
                543.0948648254819
            ]
        }
    }

    def on_button_clicked(widget, *args):
        """Dump the JSON thing."""
        print(len(args))
        print(json.dumps(args[0].values, indent=3, cls=MyEncoder))

    win = Gtk.Window()
    win.connect("destroy", Gtk.main_quit)
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    win.add(box)

    value = DictDialog(result)
    win.set_property("height-request", 500)
    scrolled = Gtk.ScrolledWindow()
    scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
    scrolled.add(value)
    box.pack_start(scrolled, True, True, 10)

    button = Gtk.Button(label="Click Here")
    button.connect("clicked", on_button_clicked, value)
    box.pack_start(button, False, False, 0)

    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
