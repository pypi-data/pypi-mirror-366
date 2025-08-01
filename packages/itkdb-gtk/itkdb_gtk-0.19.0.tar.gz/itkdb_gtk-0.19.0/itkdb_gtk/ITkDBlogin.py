"""GUI to login to the DB."""
import getpass
import json
import os
import sys
import tempfile
import threading
import time
from pathlib import Path

import gi
import itkdb
from requests.status_codes import codes

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, GObject

gtk_runs, gtk_args = Gtk.init_check()


class TimeoutCaller(threading.Timer):
    """A recursive timer."""

    def run(self):
        """Thread function."""
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)


def run_login_window(dlg):
    """Open the login dialog window in a callback."""
    if not dlg.has_window:
        dlg.create_window()

    dlg.in_callback = True
    dlg.ac1.set_text("")
    dlg.ac2.set_text("")
    dlg.show_all()
    dlg.run()
    dlg.hide()
    dlg.in_callback = False

    access1 = dlg.ac1.get_text()
    access2 = dlg.ac2.get_text()

    if access1 is None or access2 is None:
        dlg.complain("Bad Access codes.", "Not valid or empty access codes.")
        dlg.code = -2
        return

    dlg.user._access_code1 = access1
    dlg.user._access_code2 = access2
    dlg.has_to_wait = False

    dlg.set_new_credentials()
    return False


class ITkDBlogin(Gtk.Dialog):
    """Dialog to connect to the DB."""

    __gsignals__ = {
        'new_login': (GObject.SignalFlags.RUN_FIRST, None, (str, ))
    }

    def __init__(self, *args, **kwargs):
        """Initialization."""
        global gtk_runs
        if gtk_runs:
            super().__init__(*args, **kwargs)

        self.user = itkdb.core.User()
        self.code = -1
        self.has_to_wait = False
        self.in_callback = False
        self.token = None
        self.id_token = None
        self.has_window = False
        self.token_file = Path(tempfile.gettempdir(), ".itk_dbtoken")
        self.T = TimeoutCaller(30, self.reconnect)

        if os.path.exists(self.token_file):
            with open(self.token_file, 'r') as token_file:
                self.token = json.loads(token_file.read())

            if self.token:
                self.setToken()

        if self.token:
            self.T.start()
            return

        if gtk_runs:
            self.create_window()
            self.present()
            self.run()

        else:
            access1 = getpass.getpass("Access 1: ")
            access2 = getpass.getpass("Access 2: ")
            self.user._access_code1 = access1
            self.user._access_code2 = access2
            try:
                self.user.authenticate()
            except Exception:
                print("Could not connect to DB with provided credentials.")
                sys.exit()

            self.token = {
                "access_token": self.user._access_token,
                "id_token": self.user._raw_id_token,
                "issued_at": float(time.time()),
                "expires_at": self.user.expires_at
            }
            with open(self.token_file, 'w') as token_file:
                token_file.write(json.dumps(self.token))

    def do_new_login(self, *args):
        """New login."""
        pass

    def die(self):
        """Kill the timer."""
        self.T.cancel()

    def is_connected(self):
        """Tell if there is connection to DB."""
        return self.token is not None

    def reconnect(self, check=True, force=False):
        """REconnect."""
        if not force and check:
            if not self.checkTokenExpired():
                return

        set_new_cred = True
        if force or (self.user._access_code1 == "" or self.user._access_code2 == ""):

            if Gtk.main_level():
                self.has_to_wait = True
                GLib.idle_add(run_login_window, self)
                set_new_cred = False
                while not force and self.has_to_wait:
                    time.sleep(0.1)

            else:
                access1 = getpass.getpass("Access 1: ")
                access2 = getpass.getpass("Access 2: ")
                self.user._access_code1 = access1
                self.user._access_code2 = access2

            if self.code == -2:
                self.code = -1
                print("User cancelled login")
                self.die()
                sys.exit()

        if set_new_cred:
            self.set_new_credentials()

    def set_new_credentials(self):
        """Set new credentials."""
        self.user._access_token = None
        self.user._raw_id_token = None
        self.user._id_token = None
        try:
            self.user.authenticate()
            self.token = {
                "access_token": self.user._access_token,
                "id_token": self.user._raw_id_token,
                "issued_at": float(time.time()),
                "expires_at": self.user.expires_at
            }

            with open(self.token_file, 'w') as token_file:
                token_file.write(json.dumps(self.token))

            self.emit("new_login", "<OK>")

        except Exception as E:
            self.emit("new_login", str(E))

    def setToken(self):
        """Set the token things."""
        if self.checkTokenExpired():
            self.token = None
            return

        self.user._status_code = codes['ok']
        self.user._access_token = self.token['access_token']
        self.user._raw_id_token = self.token['id_token']
        self.user._id_token = self.user._raw_id_token
        self.user._parse_id_token()
        self.user._session.headers.update({'Authorization': 'Bearer {0:s}'.format(self.user.bearer)})

    def checkTokenExpired(self):
        """Check if token is expired."""
        if self.token is None:
            return True

        try:
            if not self.user.is_authenticated():
                delta = self.token['expires_at'] - time.time() - 2*self.T.interval
            else:
                delta = self.user.expires_in - 2 * self.T.interval

            return delta <= 0

        except KeyError:
            return True

    def create_window(self):
        """Create the window."""
        # set border width
        self.set_border_width(10)

        #
        self.has_window = True
        self.add_buttons(
            Gtk.STOCK_OK, Gtk.ResponseType.OK, Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL
        )
        # self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)

        self.set_title("Login to the ITk DB")

        mainBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.get_content_area().add(mainBox)

        title = Gtk.Label()
        title.set_markup('<b>ATLAS ITk Production Database Login</b>')
        mainBox.pack_start(title, True, True, 5)

        grid = Gtk.Grid(column_spacing=5, row_spacing=5)
        mainBox.pack_start(grid, True, True, 5)

        irow = 0
        self.ac1 = Gtk.Entry()
        self.ac2 = Gtk.Entry()
        self.ac1.set_visibility(False)
        self.ac2.set_visibility(False)

        grid.attach(Gtk.Label(label="Access Code 1"), 0, irow, 1, 1)
        grid.attach(self.ac1, 1, irow, 1, 1)
        irow = irow + 1
        grid.attach(Gtk.Label(label="Access Code 2"), 0, irow, 1, 1)
        grid.attach(self.ac2, 1, irow, 1, 1)

        btn = self.get_widget_for_response(Gtk.ResponseType.OK)
        btn.connect("clicked", self.on_run)

        self.show_all()

    def complain(self, main_title, second_text):
        """Opens an error dialog.

        Args:
            main_title: Main text in window
            second_text: Second text

        """
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=main_title,
        )
        dialog.format_secondary_text(second_text)
        dialog.run()
        dialog.destroy()

    @property
    def name(self):
        """Return User DB name."""
        return self.user.name

    def on_run(self, widget):
        """OK button clicked."""
        if self.in_callback:
            return

        print("logging in")
        access1 = self.ac1.get_text()
        access2 = self.ac2.get_text()

        if access1 is None or access2 is None:
            self.complain("Bad Access codes.", "Not valid or empty access codes.")
            self.code = -2
            return

        else:
            self.user._access_code1 = access1
            self.user._access_code2 = access2
            self.reconnect(False)
            if not self.T.is_alive():
                self.T.start()
            # self.user.authenticate()
            # self.token = {
            #     "access_token": self.user._access_token,
            #     "id_token": self.user._raw_id_token,
            #     "issued_at": float(time.time()),
            #     "expires_at": self.user.expires_at
            # }

            # with open('.itk_dbtoken', 'w') as token_file:
            #     token_file.write(json.dumps(self.token))
            self.hide()

    def get_client(self, use_eos=True):
        """Return the client."""
        if not self.is_connected():
            return None

        return itkdb.Client(user=self.user, use_eos=use_eos)

    def __del__(self):
        """Delete."""
        self.die()


if __name__ == "__main__":
    # Initialize the session in the ITk PDB
    dlg = ITkDBlogin()
    client = dlg.get_client()
    if client is None:
        print("Could not connect to DB with provided credentials.")
        sys.exit()

    # payload = {
    #     "project": "S",
    #     "componentType": "MODULE",
    #     "testType": "GLUE_WEIGHT"
    # }
    # lst = client.get("listTestRunsByTestType", json=payload)
    # for l in enumerate(lst):
    #     print(l)

    print("Hello {}".format(dlg.name))

    rc = client.get("getUser", json={"userIdentity": dlg.user.identity})
    print(rc)

    if gtk_runs:
        try:
            while True:
                time.sleep(0.25)

        except Exception:
            print("Arrgs")

    else:
        print("Logged on an ascii terminal.")

    dlg.die()
