"""Utilities for the inteaction with the ITkDB."""
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path
import getpass

import dateutil.parser
import itkdb

# The response of the DB
db_response = ""
attachment_urls = {}
uploaded_test_runs = []


# define an Attachment object.
class Attachment(object):
    """Encapsulates Attachment information."""

    def __init__(self, path=None, url=None, title=None, desc=None):
        """Initialization."""
        if path is not None:
            self.path = Path(path).expanduser().resolve()
            self.type = "file"
        else:
            self.path = None

        if url is not None:
            self.url = url
            self.type = "link"
        else:
            self.url = None

        if self.path and self.url:
            raise ValueError("Invalid Attachment. Has both file and link.")

        self.title = title
        self.desc = desc


def is_iterable(obj):
    """Tell if an object is iterable. Strings are not considered iterables."""
    if isinstance(obj, Iterable):
        if isinstance(obj, str) or isinstance(obj, bytes):
            return False
        else:
            return True
    else:
        return False


def get_db_response():
    """Return the DB response.

    It is stores in a global variable. Trust the function if call
    right after your interaction with the DB.
    """
    return db_response


def get_db_date(timestamp=None):
    """Convert a date string into the expected DB format.

    Args:
        timestamp: A date in string format

    """
    def date2string(the_date):
        out = the_date.isoformat(timespec='milliseconds')
        if out[-1] not in ['zZ']:
            out += 'Z'

        return out
        # return the_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")

    out = None
    if timestamp is None:
        out = date2string(datetime.now())
    elif isinstance(timestamp, datetime):
        out = date2string(timestamp)
    else:
        try:
            this_date = dateutil.parser.parse(timestamp)
            out = date2string(this_date)

        except (OverflowError, dateutil.parser.ParserError):
            out = ""

    return out



def get_petal_core_batches(session):
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

def set_petal_core_batch(session, petal_core):
    """Set the batch of the petal core."""
    if isinstance(petal_core["type"], str):
        tp = petal_core["type"]
    else:
        tp = petal_core["type"]["code"]

    if tp != "CORE_AVS":
        return

    batch_list = get_petal_core_batches(session)
    aliasID = petal_core["alternativeIdentifier"]
    if "PPB" in aliasID:
        batch_code = "PETAL_CORE_PREPROD"
    elif "PPC" in aliasID:
        batch_code = "PETAL_CORE_PROD"
    else:
        batch_code = "PETAL_CORE_PROTO"

    rc = session.post("addBatchComponent", json={"id":batch_list[batch_code], "component": petal_core["id"]})
    return rc


def registerPetalCore(client, SN, alias, HC_id=None, petal_core=None):
    """Register a Petal Core in the DB.

    Args:
        SN: Serial Number
        alias: The alias of the Petal
        HC_id: Comma separated list of HC identifiers.

    Returns:
        _type_: _description_

    """
    global db_response
    dto = {
        "project": 'S',
        "subproject": "SE",
        "institution": "AVS",
        "componentType": "CORE_PETAL",
        "type": "CORE_AVS",
        "serialNumber": SN,
        "properties": {'PRODUCTION_ID': alias}
    }
    if HC_id is not None:
        dto["properties"]["HC_ID"] = HC_id

    the_component = None

    try:
        if petal_core is None:
            db_response = client.post('registerComponent', json=dto)
            petal_core = db_response['component']

        else:
            # WE set the alternative ID and the HC_ID
            the_component = SN
            if petal_core["alternativeIdentifier"] is None:
                dto = {
                    "component": SN,
                    "code": "PRODUCTION_ID",
                    "value": alias
                }
                db_response = client.post("setComponentProperty", json=dto)

            if HC_id is not None:
                dto = {
                    "component": SN,
                    "code": "HC_ID",
                    "value": HC_id
                }
                db_response = client.post("setComponentProperty", json=dto)

        set_petal_core_batch(client, petal_core)
        return petal_core

    except KeyError:
        return None


def create_component_attachment(client, SN, file_path, title=None, description="", item_type="component"):
    """Create an attachment to the given component.

    Args:
        client: The DB client
        SN: The SN of the component.
        file_path: The pat to th efile to be attached.
        title: title of the file
        description: Description of the attachment
        item_type: the type of DB object to attach the information

    """
    global db_response
    db_response = None
    path = Path(file_path).expanduser().resolve()
    filetype =   itkdb.utils.get_mimetype(path, None)
    if title is None:
        title = path.name

    if item_type == "component":
        c_item = "component"
        cmmd = "createComponentAttachment"

    elif item_type == "shipment":
        c_item = "shipment"
        cmmd = "createShipmentAttachment"

    else:
        print("Unknown dB object")
        db_response = None
        return

    data = {
        c_item: SN,
        'title': title,
        'description': description,
        'type': 'file',
        'url': path.as_uri(),
    }
    # Get attachment data
    attachment = {'data': (path.name, open(path.as_posix(), 'rb'), filetype)}
    try:
        db_response = client.post(cmmd, data=data, files=attachment)

    except Exception as e:
        print("Error creating attachment\n", e)

    return db_response


def set_component_property(client, SN, the_property, value):
    """Set the value of an object property.

    Args:
        client: The DB client
        SN: The object SN
        the_property: The property name
        value: The property value

    """
    global db_response
    try:
        db_response = client.post('setComponentProperty',
                                  json={'component': SN,
                                        'code': the_property,
                                        'value': value})
        return db_response

    except Exception as e:
        print("Problems setting {} to {} in {}:\n\t{}".format(
            property, value, SN, str(e)))
        return None


def assemble_component(client, parent, child):
    """Assemble child into parent.

    Args:
        client: The DB client
        parent: The parent object or container.
        child: The child to be assembled.

    """
    global db_response
    try:
        db_response = client.post("assembleComponent",
                                  json={'parent': parent, 'child': child})
        return db_response

    except Exception as e:
        print("Problems assemblying {} into {}:\n\t{}".format(
            child, parent, str(e)))
        return None


def set_object_stage(client, SN, stage):
    """Set stage of object

    Args:
        client: DB session
        SN: Serial number
        stage: Stage

    """
    global db_response
    try:
        db_response = client.post("setComponentStage",
                                  json={"component": SN, "stage": stage})
        return db_response

    except Exception as e:
        print("Problems changing stage of {} into {}:\n\t{}".format(
            SN, stage, str(e)))
        return None


def get_DB_component(client, SN):
    """Get ta component by its serial number."""
    global db_response

    try:
        db_response = client.get("getComponent", json={"component": SN})
        return db_response

    except Exception as e:
        db_response = str(e)

    try:
        out = client.get('getComponent', json={'component': SN, "alternativeIdentifier":True})
        db_response = out
        return out

    except Exception as e:
        db_response = str(e)
        return None

def upload_test(client, data, attachments=None, check_runNumber=False):
    """Upload a test to the DB.

    Args:
        client: The DB client
        data (dict): A dictionary with all the elements of thee test.
        attachments ([Attachment]): one or more (in a list) Attachment to the test

    Return:
        resp: The response of the DB session.

    """
    global db_response
    global attachment_urls
    global uploaded_test_runs

    uploaded_test_runs = []
    attachment_urls = {}
    db_response = None

    # Check the given run_number. If already existing, give another one which
    # will try to be consecutive.
    if check_runNumber:
        # Get all the runNumbers in this test
        test_list = client.get("listTestRunsByComponent",
                               json={
                                    "filterMap":{
                                    "serialNumber": data["component"],
                                    "state": "ready",
                                    "testType":[data["testType"]]
                                    }
                                }
                               )
        runN= {}
        for T in test_list:
            runN[T["runNumber"]] = 1

        if data["runNumber"] in runN:
            # if the given runNumber is there, try to create a new one.
            #print("runNumber {} already in {} of {}".format(data["runNumber"], data["testType"], data["component"]))
            try:
                irun = int(data["runNumber"])
                for i in range(irun+1, 100):
                    newRn = "{}".format(i)
                    if newRn not in runN:
                        data["runNumber"] = newRn
                        break

            except ValueError:
                for i in range(100):
                    newRn = "{}_{}".format(data["runNumber"], i+1)
                    if newRn not in runN:
                        data["runNumber"] = newRn
                        break

    # Try to upload the test
    try:
        db_response = client.post("uploadTestRunResults", json=data)
        testRun = db_response["testRun"]["id"]
        uploaded_test_runs.append(testRun)

    except Exception as e:
        msg = "Could not upload the test:\n{}".format(str(e))
        return msg

    try:
        # Handle attachments.
        attachment_urls = {}
        if attachments is not None:
            if not isinstance(attachments, Iterable):
                attachments = (attachments)

            for att in attachments:
                data = {"testRun": testRun,
                        "title": att.title if att.title is not None else path.name,
                        "description": att.desc if att.desc is not None else path.name,
                        "type": att.type,
                        }
                if att.type == "file":
                    path = Path(att.path).expanduser().resolve()
                    if not path.exists():
                        print("File {} does not exist".format(path))
                        continue

                    data["url"] = path.as_uri()
                    filetype = itkdb.utils.get_mimetype(path.as_posix(), None)
                    attachment = {'data': (path.as_posix(), open(path.as_posix(), 'rb'), filetype)}
                else:
                    data["url"] = att.url
                    filetype = itkdb.utils.get_mimetype(att.url, None)
                    attachment = {'data':(att.url, None, "text/x-uri") }

                db_response = client.post('createTestRunAttachment',
                                          data=data,
                                          files=attachment)
                try:
                    url = db_response['url'].replace("https://eosatlas.cern.ch","https://cernbox.cern.ch/files/spaces")
                    attachment_urls[path.name] = url

                except KeyError:
                    pass


        return None

    except Exception as e:
        return "Could not upload attachment:\n{}".format(str(e))


def set_test_run_parameter(session, test_run, parameter, value):
    """Modify testRun Parameter

    Args:
        session: The ITkDB session
        test_run: ID of test run
        parameter: parameter code
        value: The new value
    """
    global db_response
    try:
        db_response = session.post("setTestRunParameter",
                                   json={"testRun": test_run, "code": parameter, "value": value})
        return None

    except Exception as E:
        return (str(E))

def create_test_run_comment(session, test_run, comments):
    """Adds a new comment in testRun."""
    global db_response
    if not isinstance(comments, Iterable):
        comments = (comments)

    try:
        db_response = session.post("createTestRunComment", json={"testRun": test_run, "comments": comments})
        return None

    except Exception as E:
        return (str(E))

def create_shipment(session, sender, recipient, items, name=None, send=False,
                    shipment_type="domestic", attachment=None, comments=None):
    """Create a chipment.

    Args:
        session : The itkdb session
        sender : The sender ID
        recipient : The recipient ID
        items : A list of SN of the items to be shipped.
        name: the name of the shipment.
        send: If true, the status of the shipment is updated to inTransit
        type (optional): Type of shipment. Defaults to "domestic".
        attachment (optional, :class:`Attachment`): :class:`Attachment` object.
        comments (optional): comments for the shipment

    """
    global db_response
    if name is None:
        name = "From {} to {}".format(sender, recipient)

    if shipment_type not in ["domestic", "intraContinental", "continental"]:
        db_response = "Wrong shipment type."
        return None

    if len(items) == 0:
        db_response = "Empty lit of items"
        return None

    the_comments = None
    if comments is not None:
        if not is_iterable(comments):
            the_comments = [comments]
        else:
            the_comments = comments

    data = {
        "name": name,
        "sender": sender,
        "recipient": recipient,
        "type": shipment_type,
        "shipmentItems": items,
    }

    if the_comments:
        data["comments"] = the_comments

    try:
        db_response = session.post("createShipment", json=data)

    except Exception as E:
        db_response = str(E)
        return None

    if not send:
        return db_response

    shipment_id = db_response["id"]
    payload = {
        "shipment": shipment_id,
        "status": "inTransit",
    }

    # The items
    items = []
    for item in db_response["shipmentItems"]:
        the_item = {"code": item['code'], "delivered": True}
        items.append(the_item)

    payload["shipmentItems"] = items

    db_response = None
    try:
        db_response = session.post("setShipmentStatus", json=payload)

    except Exception as E:
        db_response = str(E)
        return None

    if attachment:
        try:
            rc = create_component_attachment(session, shipment_id,
                                             attachment.path,
                                             attachment.title,
                                             attachment.desc,
                                             "shipment")
            db_response = rc

        except Exception:
            db_response = "Could not add the attachment."

    return db_response


def set_shipment_status(client, data):
    """Update shipment status."""
    global db_response
    try:
        db_response = client.post("setShipmentStatus", json=data)
        return db_response

    except Exception:
        return None


def from_full_test_to_test_data(full_test):
    """Conver getTest output to json needed to upload the test."""
    test = {
        "component": None,
        "testType": full_test["testType"]["code"],
        "institution": full_test["institution"]["code"],
        "runNumber": full_test["runNumber"],
        "date": full_test["date"],
        "passed": full_test["passed"],
        "problems": full_test["problems"],
        "properties": {},
        "results": {},
        "comments": [],
        "defects": []
    }

    try:
        test["component"] = full_test["components"][0]["serialNumber"]

    except Exception:
        print("from_full_test_to_test_data\nPossible error: no SN found for component.")
        pass

    for P in full_test["properties"]:
        test["properties"][P["code"]] = P['value']

    if full_test["results"]:
        for P in full_test["results"]:
            test["results"][P["code"]] = P['value']

    if full_test["comments"]:
        for C in full_test["comments"]:
            test["comments"].append(C["comment"])

    if full_test["defects"]:
        for D in full_test["defects"]:
            test["defects"].append({"name": D["name"],
                                    "description": D["description"],
                                    "properties": D["properties"]})

    return test


def get_testrun(session, test_id, out_type="object"):
    """Retrieve information about a given test.

    Args:
        session : The itkdb session
        test_id : The ID of the test.
        out_type (optional): Type of output (full or object). Defaults to "object".

    """
    global db_response
    try:
        db_response = session.get("getTestRun", json={"testRun": test_id})
        return db_response

    except Exception:
        return None


def get_test_skeleton(session, component, test_code, userdef=None, uservalues=None):
    """Get the skeleton of the given test.

    Args:
        session: The DB session
        component: The component which is tested
        test_code: The test code
        userdef: default values of test parameters, propertines and results.
        uservalues: default values for different types.

    """
    global db_response

    if userdef is None:
        userdef = {}

    if uservalues is None:
        uservalues = {}

    defvalues = {
        "string": "",
        "integer": -9999,
        "float": -9999.0,
        "boolean": True,
    }
    for ky, val in defvalues.items():
        if ky not in uservalues:
            uservalues[ky] = val

    data = {"project": "S", "componentType": component}
    out = session.get("listTestTypes", json=data)
    db_response = out
    the_test = None
    for tst in out:
        # print(tst['code'])
        if tst['code'] == test_code:
            the_test = tst
            break

    if the_test is None:
        print("test {} not found for {}".format(test_code, component))
        return None

    # for prop in the_test["properties"]:
    #     print("{}; {}".format(prop["code"], prop["name"]))

    # for prop in the_test["parameters"]:
    #     print("{}; {}".format(prop["code"], prop["name"]))

    skltn = {
        "component": None,
        "testType": test_code,
        "institution": None,
        "runNumber": "-1",
        "date": get_db_date(),
        "passed": True,
        "problems": False,
        "properties": {},
        "results": {},
        "comments": [],
        "defects": []
    }

    # Set default values
    for key, val in skltn.items():
        if key in userdef:
            if isinstance(val, dict):
                continue

            skltn[key] = userdef[key]

    def get_default(vin, default=None):
        # print(json.dumps(vin, indent=1))
        if vin['valueType'] == "single":
            vtype = vin['dataType']
            val = None
            if vtype in uservalues:
                val = uservalues[vtype]
            else:
                # print("default for data type ", vtype, " not found")
                val = None

        else:
            val = None

        return val

    # SEt the properties
    for prop in the_test['properties']:
        key = prop["code"]
        if 'properties' in userdef and key in userdef['properties']:
            skltn['properties'][key] = userdef['properties'][key]
        else:
            skltn['properties'][key] = get_default(prop)

    # SEt the parameters
    for par in the_test['parameters']:
        key = par["code"]
        if 'results' in userdef and key in userdef['results']:
            skltn['results'][key] = userdef['results'][key]
        else:
            skltn['results'][key] = get_default(par)

    return skltn

def create_client():
    """Create a Client."""
    client = itkdb.Client()
    client.user._access_code1 = getpass.getpass("Access 1: ")
    client.user._access_code2 = getpass.getpass("Access 2: ")
    client.user.authenticate()
    print("Hello {} !".format(client.user.name))
    return client

def get_db_user(client):
    """REturn PDB information of current user.

    Args:
        client (itkdb.Client): The DB client.

    """
    global db_response
    if client is None:
        return None

    try:
        db_response = client.get("getUser", json={"userIdentity": client.user.identity})
        return db_response
    except Exception:
        return None
