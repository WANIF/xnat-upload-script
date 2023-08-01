#!/usr/bin/python3

# Script to upload all DICOM files from a given folder to XNAT, then delete them from said folder.
# To be run e.g. hourly or daily to update XNAT with new scans.
# Configure paravision to automatically export all DICOMs to a given folder (probably one per
# user for privacy reasons but not necessarily).

# Run using the following syntax: $ xnat_upload_REST.py [directory]

# Needs a username/password ~/.netrc to connect, with permission 600, with the following syntax:

# machine xnat-mri.cmca.uwa.edu.au
#         login admin
#         password <password>
#

import glob
import os
import sys
import xnat

# Exit if usage is incorrect
if len(sys.argv) != 2:
    print("Usage: $ xnat_upload_REST.py [directory]")
    exit(1)

## Definitions

# scandir - the directory we are uploading images from
# Exit if directory doesn't exist
scandir = sys.argv[1]
if not os.path.isdir(scandir):
    print(f"{scandir} does not exist or is not a directory.")
    exit(1)

# Uploads a dicom file to XNAT.
def upload_file(srvc, filepath, overwrite="delete"):
    # srvc = connection service.
    # filepath = path and filename.
    # overwrite = how to handle existing data: append, delete, or none.

    # Dictionary containing query options.
    query = {}

    # Should we overwrite files? default=yes aka delete.
    if overwrite is not None:
        query['overwrite'] = overwrite
    # Import method - use gradual-DICOM for standard XNAT import path.
    query['import_handler'] = "gradual-DICOM"
    # Should DICOM files be renamed according to XNAT schema (yes).
    query['rename'] = "true"
    # Directly upload to archive (skip the prearchive)
    query['direct_archive'] = "true"
    # The uri aka the REST interface to use
    uri = '/data/services/import'

    # Error if the file doesn't exist
    if not os.path.exists(filepath):
        raise FileNotFoundError("The file you are trying to import does not exist.")
        exit(1)

    # Guess content type (will probably be application/dicom)
    content_type = srvc.guess_content_type(filepath)

    # Run the command, and save the response
    # response=200 if successful
    response = srvc.xnat_session.upload_file(uri=uri, path=filepath, query=query, content_type=content_type, method='post')
    response_text = response.text.strip()
    # Raise an error if return code is not successful, otherwise assume all is good!
    if response.status_code != 200:
        raise xnat.exceptions.XNATResponseError('The response for uploading was ({}) {}'.format(response.status_code, response.text))


# Create the xnat connection, and use it in a context to ensure clean connection closure
with xnat.connect('https://xnat-mri.cmca.uwa.edu.au') as session:

    # Create the xnat service object to use upload actions.
    srvc = xnat.services.Services(session)

    # Upload and then delete each dicom file
    for f in glob.glob(f"{scandir}/**/*.dcm", recursive=True):
        try:
            upload_file(srvc, f, overwrite="delete")
            os.remove(f)
        except Exception as e:
            print(f"Failed to upload: {str(e)}")





    

