#!/usr/bin/env python3
"""A set of utilities for teh warp scanner."""
import pathlib
import serial
import serial.tools.list_ports as list_ports

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import GLib

class QRScanner:
    """Contains information to detect the scanner."""
    def __init__(self, callback):
        self.reader = None
        self.callback = callback
        self.timer_id = None
        self.source_id = None
        self.init_scanner()

    def init_scanner(self):
        """Sets the scanner."""
        self.setup_scanner()
        if self.reader is None:
            self.timer_id = GLib.timeout_add(500, self.find_scanner)
        else:
            print("Found scanner in {}".format(self.reader.name))

    def find_scanner(self, *args):
        """Check if the scanner is there."""
        # if the reader is there, stop the timeput
        if self.reader is not None:
            return False

        # Try to setup the scanner
        self.setup_scanner()
        if self.reader is not None:
            self.timer_id = None
            print("Found scanner in {}".format(self.reader.name))
            return False
        else:
            return True


    def setup_scanner(self):
        """Setup scanner and callback function."""
        if self.reader is not None:
            return

        self.reader = None
        device_signature = '05f9:4204'
        candidates = list(list_ports.grep(device_signature))
        if not candidates:
            return

        self.reader = serial.Serial(candidates[0].device, 9600)
        self.source_id = GLib.unix_fd_add_full(
                GLib.PRIORITY_DEFAULT,
                self.reader.fileno(),
                GLib.IOCondition.IN | GLib.IOCondition.ERR | GLib.IOCondition.NVAL,
                self.get_line,
                self.callback,
                )


    def finish_timeout(self):
        """Finishes the timeout."""
        GLib.source_remove(self.source_id)
        self.source_id = None

        self.reader.close()
        self.reader = None

        # re-start the search of the scanner
        self.timer_id = GLib.timeout_add(500, self.find_scanner)

    def get_line(self, fd, state, callback):
        """Has to info to read."""
        if state == GLib.IOCondition.IN:
            try:
                available = self.reader.in_waiting
                while True:
                    delta = self.reader.in_waiting - available
                    if not delta:
                        break

                # Get data from serial device passed in via
                data = self.reader.read_until(expected='\r', size=self.reader.in_waiting).strip()
                txt = data.decode('utf-8')
                if callback:
                    callback(txt)

            except OSError:
                if not pathlib.Path(self.reader.name).exists():
                    print("Device unplugged.")
                    self.finish_timeout()
                    return False

            return True


        else:
            self.finish_timeout()
            return False

def get_text_from_scanner(txt):
    """Callback where the scanners sends the text."""
    print("### {}".format(txt))

def test_scanner():
    """Test the thing."""
    scanner = QRScanner(get_text_from_scanner)
    loop = GLib.MainLoop()
    try:
        loop.run()
    except KeyboardInterrupt:
        loop.quit()

if __name__ == "__main__":
    test_scanner()
