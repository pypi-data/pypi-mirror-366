#!/usr/bin/env python3
"""Test dashboard."""
import sys

try:
    import itkdb_gtk

except ImportError:
    from pathlib import Path
    cwd = Path(__file__).parent.parent
    sys.path.append(cwd.as_posix())


from itkdb_gtk import dbGtkUtils
from itkdb_gtk import GetShipments
from itkdb_gtk import ITkDBlogin
from itkdb_gtk import CreateShipments
from itkdb_gtk import UploadTest
from itkdb_gtk import UploadMultipleTests
from itkdb_gtk import GlueWeight
from itkdb_gtk import UploadModuleIV
from itkdb_gtk import WireBondGui
from itkdb_gtk import PanelVisualInspection
from itkdb_gtk import VisualInspection
from itkdb_gtk import findComponent


HAS_PETALQC=False
try:
    from petal_qc.metrology.coreMetrology import CoreMetrology, CoreMetrologyOptions
    from petal_qc.thermal.coreThermal import CoreThermal
    from petal_qc.thermal.IRPetalParam import IRPetalParam
    from petal_qc.metrology.uploadPetalInformation import AVSPanel, AVSOptions
    from petal_qc import PetalReceptionTests

    HAS_PETALQC = True
except ImportError as E:
    HAS_PETALQC = False


import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

HELP_LINK="https://itkdb-gtk.docs.cern.ch"

class DashWindow(dbGtkUtils.ITkDBWindow):
    """Dashboard class."""
    UPLOAD_TEST = 1
    UPLOAD_MANY_TESTS = 2
    CREATE_SHIPMNT = 3
    RECV_SHIPMNT = 4
    PETAL_RECEPTION = 5
    GLUE_WEIGHT = 6
    MOD_IV = 7
    WIRE_BOND = 8
    PANEL_VI = 9
    MODULE_VI = 10
    PETAL_CORE_METRO = 11
    PETAL_CORE_THERMAL = 12
    PETAL_INFORMATION = 13
    FIND_COMPONENT = 14

    def __init__(self, session):
        """Initialization."""
        super().__init__(title="ITkDB Dashboard", session=session, help_link=HELP_LINK)
        self.mask = 0

        # set border width
        self.set_border_width(10)

        # Prepare dashboard
        #lbl = Gtk.Label()
        #lbl.set_markup("<big><b>ITkDB available commands.</b></big>")
        #self.mainBox.pack_start(lbl, True, True, 0)

        grid = Gtk.Grid(column_spacing=5, row_spacing=5)
        self.mainBox.pack_start(grid, False, True, 5)

        irow = 0
        lbl = Gtk.Label()
        lbl.set_markup("<b>Tests</b>")
        lbl.set_xalign(0)
        grid.attach(lbl, 0, irow, 1, 1)

        irow += 1
        btnTest = Gtk.Button(label="Upload Single Test")
        btnTest.connect("clicked", self.upload_test)
        grid.attach(btnTest, 0, irow, 1, 1)

        btnTest = Gtk.Button(label="Upload Multiple Tests")
        btnTest.connect("clicked", self.upload_multiple_tests)
        grid.attach(btnTest, 1, irow, 1, 1)

        irow +=1
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        grid.attach(separator, 0, irow, 2, 1)

        irow += 1
        btnModVI = Gtk.Button(label="Module/Sensor Visual Insp.")
        btnModVI.connect("clicked", self.module_VI)
        grid.attach(btnModVI, 0, irow, 1, 1)
        

        btnPanelVI = Gtk.Button(label="Panel Visual Insp.")
        btnPanelVI.connect("clicked", self.panel_VI)
        grid.attach(btnPanelVI, 1, irow, 1, 1)
        
        irow += 1
        btnModIV = Gtk.Button(label="Sensor/Module IV")
        btnModIV.connect("clicked", self.module_IV)
        grid.attach(btnModIV, 0, irow, 1, 1)

        btnWireBond = Gtk.Button(label="Wire Bond")
        btnWireBond.connect("clicked", self.wire_bond)
        grid.attach(btnWireBond, 1, irow, 1, 1)

        irow += 1
        btnWeight = Gtk.Button(label="GlueWeight")
        btnWeight.connect("clicked", self.glue_weight)
        grid.attach(btnWeight, 0, irow, 1, 1)



        if HAS_PETALQC:
            irow +=1
            separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
            grid.attach(separator, 0, irow, 2, 1)

            irow +=1
            btnPetalInfo = Gtk.Button(label="AVS Petal Info")
            btnPetalInfo.connect("clicked", self.upload_petal_info)
            grid.attach(btnPetalInfo, 0, irow, 1, 1)

            btnGnd = Gtk.Button(label="Petal Reception")
            btnGnd.connect("clicked", self.petal_reception)
            grid.attach(btnGnd, 1, irow, 1, 1)

            irow +=1
            btnPetalMetrology = Gtk.Button(label="Petal Core Metrology")
            btnPetalMetrology.connect("clicked", self.petal_metrology)
            grid.attach(btnPetalMetrology, 0, irow, 1, 1)

            btnPetalThermal = Gtk.Button(label="Petal Core Thermal")
            btnPetalThermal.connect("clicked", self.petal_thermal)
            grid.attach(btnPetalThermal, 1, irow, 1, 1)

        irow += 1
        grid.attach(Gtk.Label(), 0, irow, 1, 1)

        irow += 1
        lbl = Gtk.Label()
        lbl.set_markup("<b>Shipments</b>")
        lbl.set_xalign(0)
        grid.attach(lbl, 0, irow, 1, 1)

        irow += 1
        sendS = Gtk.Button(label="Create Shipment")
        sendS.connect("clicked", self.create_shipment)
        grid.attach(sendS, 0, irow, 1, 1)

        recS = Gtk.Button(label="Receive Shipment")
        recS.connect("clicked", self.receive_shipment)
        grid.attach(recS, 1, irow, 1, 1,)

        irow += 1
        lbl = Gtk.Label()
        lbl.set_markup("<b>Utils</b>")
        lbl.set_xalign(0)
        grid.attach(lbl, 0, irow, 1, 1)

        irow += 1
        findC = Gtk.Button(label="Find Component")
        findC.connect("clicked", self.find_component)
        findC.set_tooltip_text("Scan your QR or bar code and get info from DB.")
        grid.attach(findC, 0, irow, 1, 1,)


        self.mainBox.pack_start(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), False, True, 5)

        self.show_all()

    def upload_test(self, *args):
        """Launch upload test."""
        bitn = DashWindow.UPLOAD_TEST
        bt = 1 << bitn
        if self.mask & bt:
            return

        self.mask |= bt
        W = UploadTest.UploadTest(
            self.session,
            help_link="{}/uploadSingleTest.html".format(HELP_LINK)
        )
        W.connect("destroy", self.app_closed, bitn)

    def upload_multiple_tests(self, *args):
        """Launch upload multiple test."""
        bitn = DashWindow.UPLOAD_MANY_TESTS
        bt = 1 << bitn
        if self.mask & bt:
            return

        self.mask |= bt
        W = UploadMultipleTests.UploadMultipleTests(
            self.session,
            help_link="{}/uploadMultipleTests.html".format(HELP_LINK)
        )
        W.connect("destroy", self.app_closed, bitn)

    def create_shipment(self, *args):
        """Launch createShipment."""
        bitn = DashWindow.CREATE_SHIPMNT
        bt = 1 << bitn
        if self.mask & bt:
            return

        self.mask |= bt
        W = CreateShipments.CreateShipments(
            self.session,
            help_link="{}/createShipment.html".format(HELP_LINK)
        )
        W.connect("destroy", self.app_closed, bitn)

    def receive_shipment(self, *args):
        """Launch getShipments."""
        bitn = DashWindow.RECV_SHIPMNT
        bt = 1 << bitn
        if self.mask & bt:
            return

        self.mask |= bt
        W = GetShipments.ReceiveShipments(
            self.session,
            help_link="{}/receiveShipments.html".format(HELP_LINK)
        )
        W.connect("destroy", self.app_closed, bitn)


    def glue_weight(self, *args):
        """Glue Weight test."""
        bitn = DashWindow.GLUE_WEIGHT
        bt = 1 << bitn
        if self.mask & bt:
            return

        self.mask |= bt
        W = GlueWeight.GlueWeight(self.session, help_link=HELP_LINK)
        W.connect("destroy", self.app_closed, bitn)

    def module_IV(self, *args):
        """Module IV tests."""
        bitn = DashWindow.MOD_IV
        bt = 1 << bitn
        if self.mask & bt:
            return

        self.mask |= bt
        W = UploadModuleIV.IVwindow(
            self.session,
            help_link="{}/uploadModuleIV.html".format(HELP_LINK)
        )
        W.connect("destroy", self.app_closed, bitn)

    def wire_bond(self, *args):
        """Module IV tests."""
        bitn = DashWindow.WIRE_BOND
        bt = 1 << bitn
        if self.mask & bt:
            return

        self.mask |= bt
        W = WireBondGui.WireBond(
            session=self.session,
            title="Wirebond",
            help_link="{}//wirebondTest.html".format(HELP_LINK),
        )
        W.connect("destroy", self.app_closed, bitn)
        W.show_all()

    def panel_VI(self, *args):
        """Panel VI tests."""
        bitn = DashWindow.PANEL_VI
        bt = 1 << bitn
        if self.mask & bt:
            return

        self.mask |= bt
        W = PanelVisualInspection.PanelVisualInspection(
            session=self.session,
            title="Panel Visual Inspection",
            help_link="{}/panelVisualInspection.html".format(HELP_LINK),
        )
        W.connect("destroy", self.app_closed, bitn)
        W.show_all()

    def module_VI(self, *args):
        """Panel VI tests."""
        bitn = DashWindow.MODULE_VI
        bt = 1 << bitn
        if self.mask & bt:
            return

        self.mask |= bt
        W = VisualInspection.ModuleVisualInspection(
            session=self.session,
            title="Module/Sensor Visual Inspection",
            help_link="{}/moduleVisualInspection.html".format(HELP_LINK),
        )
        W.connect("destroy", self.app_closed, bitn)
        W.show_all()
        
        
    def find_component(self, *args):
        """Find Component."""
        bitn = DashWindow.FIND_COMPONENT
        bt = 1 << bitn
        if self.mask & bt:
            return

        W = findComponent.FindComponent(
            self.session,
            help_link="{}/findComponent.html".format(HELP_LINK)
            )
        
        W.connect("destroy", self.app_closed, bitn)
        
    def petal_reception(self, *args):
        """Petal GND/VI test."""
        bitn = DashWindow.PETAL_RECEPTION
        bt = 1 << bitn
        if self.mask & bt:
            return

        self.mask |= bt
        W = PetalReceptionTests.PetalReceptionTests(
            self.session,
            help_link="{}/petalReceptionTests.html".format(HELP_LINK)
        )
        W.connect("destroy", self.app_closed, bitn)


    def upload_petal_info(self, *srgs):
        """Upload petal Info."""
        if not HAS_PETALQC:
            return

        bitn = DashWindow.PETAL_INFORMATION
        bt = 1 << bitn
        if self.mask & bt:
            return

        self.mask |= bt
        W = AVSPanel(self.session, AVSOptions())
        W.connect("destroy", self.app_closed, bitn)
        W.show_all()

    def petal_metrology(self, *args):
        """Do petal metrology"""
        if not HAS_PETALQC:
            return

        bitn = DashWindow.PETAL_CORE_METRO
        bt = 1 << bitn
        if self.mask & bt:
            return

        self.mask |= bt
        opts = CoreMetrologyOptions()
        W = CoreMetrology(opts, session=self.session, title="Petal Core Metrology")
        W.connect("destroy", self.app_closed, bitn)
        W.show_all()

    def petal_thermal(self, *args):
        """Do petal thermal."""
        if not HAS_PETALQC:
            return

        bitn = DashWindow.PETAL_CORE_THERMAL
        bt = 1 << bitn
        if self.mask & bt:
            return

        self.mask |= bt
        opt = IRPetalParam()
        opt.files = []
        opt.golden = None
        opt.folder = None
        opt.out = None
        opt.alias = None
        opt.SN = None
        opt.desy = False
        W = CoreThermal(opt, self.session, title="Petal Thermal Test.")
        W.connect("destroy", self.app_closed, bitn)
        W.show_all()

    def app_closed(self, *args):
        """Application window closed. Clear mask."""
        bt = 1 << args[1]
        self.mask &= ~bt
        # print(bt, self.mask)


def main():
    """main entry."""
    # DB login
    dlg = ITkDBlogin.ITkDBlogin()
    client = dlg.get_client()
    if client is None:
        print("Could not connect to DB with provided credentials.")
        dlg.die()
        sys.exit()

    client.user_gui = dlg

    dashW = DashWindow(client)
    dashW.connect("destroy", Gtk.main_quit)
    try:
        Gtk.main()

    except KeyboardInterrupt:
        print("Arrrgggg!!!")

    dlg.die()


if __name__ == "__main__":
    main()
