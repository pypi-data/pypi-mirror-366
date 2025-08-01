""" itkdb-gtk python module
"""
__version__ = "0.18.0.dev3"


def dash_board():
    """Launches the dash board."""
    from .dashBoard import main
    dashBoard.main()


def getShipments():
    """getShipments."""
    from .GetShipments import main
    main()


def glueWeight():
    """glue weight."""
    from .GlueWeight import main
    main()

def createShipments():
    """Send items."""
    from .CreateShipments import main
    main()

def uploadTest():
    """Upload a single tests."""
    from .UploadTest import main
    main()


def uploadMultipleTests():
    """Upload multiple tests."""
    from .UploadMultipleTests import main
    main()

def uploadModuleIV():
    """Upload IV files of single and double modules"""
    from .UploadModuleIV import main
    main()

def wirebondTest():
    """Inputs data and eventually upload wirebod test."""
    from .WireBondGui import main
    main()

def panelVisualInspection():
    """Visual inspection of PWB or HYB panels."""
    from .PanelVisualInspection import main
    main()

def visualInspection():
    """Visual inspection of Modules/Sensors."""
    from .VisualInspection import main
    main()

def findDBComponent():
    """Find object from QR or bar code"""
    from .findComponent import main
    main()
