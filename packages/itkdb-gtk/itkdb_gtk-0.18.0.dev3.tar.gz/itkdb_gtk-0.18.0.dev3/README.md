# Interaction with the ITk PDB.

This folder contains a collection of scripts that help interacting with the DB
using a Gtk based GUI, which includes a first attempt of reauthentication.

You need to install itkdb and serial. The former for obvious reasons. The latter
to handle a WASP QR reader to create/receive shipments.

Also needed to run is python-dateutil.

## dbGtkUtils.py
A collections of utilities to show/edit in the GUI the values of the JSON files to be
uploaded to the DB and to create the application windows.

## ITkDButils.py
Contains a larga fraction of utility functions to "talk" to the DB.

## ITkDBlogin.py
Provides a GUI interface to provide credentials to the DB. The token will be
updated before expiration. This is usefull for very long sessions in the GUI.

## uploadPetalInformation.py
Reads the AVS Production Sheet and FAT reports. With this information it creates
the petal core in the DB, if not yet there, make the assembly of the components,
and uploadas the test runs made at AVS.

## UploadTest.py
A GUI to upload the JSON files corresponding to a test and, also, to add
attachmetns.

## UploadMultipleTests.py
This will allow to select various test files, or even scan a whole directory to
find them, and assign comments, defects or attachments to each of the tests found.

## GetShipments.py
Find all shipments to be received at a given site and list them. It handles a
barcode reader that helps identifying the items actually received for the
reception. It will finally make the DB aware of the items receptioned.

## CreateShipments.py
Create a new shipment. Allows to add items with the QR reader as well as from a
GUI dialog. One can add comments and attachments to the shipment.

## GroundVITests.py
Allows to upload and enter valueos, comments and defects for those items in the gounding
and visual instpections tests of the petal core.

## UploadModuleIV.py
The idea behind this is that we messure the IV on a Ring module and on only one of the to Half modules. The IV of the remaining half modules is derived from the other 2. Eventually the IV test can be uploaded to the DB.

## dashBoard.py
This is an launcher application from which we can start most of the other
applications. It is a very good starting point. There is a Gnome desktop file (ITkDB.desktop)
that needs to be copied to `$HOME/.local/share/applications` and an icon (ITkDB.svg) that
needs to go to `$HOME/.local/share/icons`
