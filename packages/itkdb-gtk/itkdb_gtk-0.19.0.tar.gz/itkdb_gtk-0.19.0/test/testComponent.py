import sys

try:
    import itkdb_gtk
    
except ImportError:
    from pathlib import Path
    cwd = Path(__file__).parent.parent
    sys.path.append(cwd.as_posix())

from itkdb_gtk import ITkDBlogin, ITkDButils

dlg = ITkDBlogin.ITkDBlogin()
client = dlg.get_client()
if client is None:
    print("Could not connect to DB with provided credentials.")
    dlg.die()
    sys.exit()

client.user_gui = dlg

ITkDButils.get_DB_component(client, "PCPTB02")

dlg.die()