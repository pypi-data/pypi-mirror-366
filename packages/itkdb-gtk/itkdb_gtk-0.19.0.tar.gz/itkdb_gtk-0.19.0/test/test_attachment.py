#!/usr/bine/env python3
"""test big attachments."""

import json
import sys
from pathlib import Path
import itkdb

try:
    import itkdb_gtk

except ImportError:
    cwd = Path(__file__).parent.parent
    sys.path.append(cwd.as_posix())

from itkdb_gtk import ITkDBlogin, ITkDButils


# DB login
dlg = ITkDBlogin.ITkDBlogin()
client = dlg.get_client(use_eos=True)
if client is None:
    print("Could not connect to DB with provided credentials.")
    dlg.die()
    sys.exit()

client.user_gui = dlg

ifile = Path("/Users/lacasta/Nextcloud/ITk/5-Petal_cores/PPC.007/Rx_PPC.007.png")
core = ITkDButils.get_DB_component(client, "PPC.007")
data = { "filterMap": { "serialNumber": core["serialNumber"], "testType":["XRAYIMAGING"]},
}

test_list = client.get("listTestRunsByComponent", json=data)
ntest = 0
for tst in test_list:
    if tst['state'] == 'ready':
        ntest += 1
        
if ntest == 0:
    defaults = {
        "institution": "IFIC",
        "runNumber": "1",
    }

    tmp = ITkDButils.get_test_skeleton(client, "CORE_PETAL", "XRAYIMAGING", defaults)
    tmp["component"] = core["serialNumber"]
    tmp["properties"]["OPERATOR"] = "Nicolas Cespedosa"
    tmp["properties"]["MACHINEID"] ="X-ray"
    print(tmp)




#client._use_eos = True 
A = ITkDButils.Attachment(path=ifile.as_posix(),  
                          title="{} X-ray".format(core["alternativeIdentifier"]),
                          desc="{} X-ray image".format(core["alternativeIdentifier"])
                            )
rc = ITkDButils.upload_test(client, data=tmp, attachments=[A])

if rc:
    ipos = rc.find("The following details may help:")
    print(rc[ipos:])
    
else:
    print("upload successful")
    
    
dlg.die()
