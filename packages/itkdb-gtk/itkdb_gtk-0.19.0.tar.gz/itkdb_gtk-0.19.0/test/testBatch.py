#!/usr/bin/env python3
"""Test Batches."""

try:
    import itkdb_gtk
    
except ImportError:
    import sys
    from pathlib import Path
    cwd = Path(__file__).parent.parent
    sys.path.append(cwd.as_posix())

from itkdb_gtk import ITkDBlogin, ITkDButils


def get_all_Petals(session):
    """Find all petal cores"""
    # find all cores
    # Now all the objects
    payload = {
        "filterMap": {
            #"componentType": ["BT"],
            "componentType": ["CORE_PETAL"],
            "type": ["CORE_AVS"],
            #"currentLocation": ["IFIC"],
        },
        "sorterList": [
            {"key": "alternativeIdentifier", "descending": False }
        ],
    }
    core_list = session.get("listComponents", json=payload)
    return core_list

def list_petal_core_batches(session):
    """Get list of Petal core batches"""
    payload = {
        "filterMap": {
            "project": "S",
            "batchType": ["PETAL_CORE_BATCH_TYPE"],
        }
    }
    batch_list = session.get("listBatches", json=payload)
    rc = {}
    for B in batch_list:
        rc[B["number"] ]= B["id"]

    return rc


def create_petal_core_batchType(session):
    """Creates the batches."""
    out = session.post(
        "createBatchType",
        json={
            "code": "PETAL_CORE_BATCH_TYPE",
            "name": "Petal Core",
            "state": "active",
            "project": "S",
        },
    )
    out = session.post(
        "createBatch",
        json={
            "project": "S",
            "batchType": "PETAL_CORE_BATCH_TYPE",
            "number": "PETAL_CORE_PROTO",
            "ownerInstituteList": ["IFIC", "AVS", "DESYHH"],
        },
    )
    out = session.post(
        "createBatch",
        json={
            "project": "S",
            "batchType": "PETAL_CORE_BATCH_TYPE",
            "number": "PETAL_CORE_PREPROD",
            "ownerInstituteList": ["IFIC", "AVS", "DESYHH"],
        },
    )
    out = session.post(
        "createBatch",
        json={
            "project": "S",
            "batchType": "PETAL_CORE_BATCH_TYPE",
            "number": "PETAL_CORE_PROD",
            "ownerInstituteList": ["IFIC", "AVS", "DESYHH"],
        },
    )


def main(session):
    """Create batchers."""
    #create_petal_core_batchType(session)
    
    batch_list = list_petal_core_batches(session)
    
#    # create the batches
#    for bc, bid in batch_list.items():
#        payload = {
#            "project": "S",
#            "batchType": bc,
#            "number": "1",
#            "ownerInstituteList": ["AVS", "IFIC", "DESYHH"]
#        }
#        rc = session.post("createBatch", json=payload)
        
    
    for petal_core in get_all_Petals(session):
        aliasID = petal_core["alternativeIdentifier"]
        if "PPB" in aliasID:
            batch_code = "PETAL_CORE_PREPROD"
        elif "PPC" in aliasID:
            batch_code = "PETAL_CORE_PROD"
        elif "test" in aliasID.lower():
            continue
        else:
            batch_code = "PETAL_CORE_PROTO"
        
        print("{} - {}".format(aliasID, batch_code))
        rc = session.post("addBatchComponent", json={"id":batch_list[batch_code], "component": petal_core["id"]})
        if rc is None:
            pass
        else:
            pass


if __name__ == "__main__":
    # ITk_PB authentication
    dlg = ITkDBlogin.ITkDBlogin()
    db_session = dlg.get_client()

    try:
        main(db_session)

    except Exception as E:
        print(E)
        
    dlg.die()
