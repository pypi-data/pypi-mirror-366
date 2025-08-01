#!/usr/bin/env python3
"""Un trash a trashed component."""


def untrash_component(client, SN, reason="Accidentally trashed"):
    """Un trash given component.

    Args:
        SN (str): Serial number of component to recover.
        reason (str): message for the DB
    Returna:
        dict: PDB response.

    """
    DTO = {
        'component': SN,
        'trashed': False,
        'reason': reason
    }

    response = client.post('setComponentTrashed', json=DTO)
    return response


if __name__ == "__main__":
    import sys
    from itkdb_gtk import ITkDBlogin
    dlg = ITkDBlogin.ITkDBlogin()
    client = dlg.get_client()

    try:
        response = untrash_component(client, sys.argv[1])

    except Exception as E:
        print(str(E))
