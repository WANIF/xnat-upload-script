#!/usr/bin/python3

# Python script to search for missing PV archives to upload.
# GENERAL CONCEPT: Links to each file are stored in a separate folder. When an archive is uploaded to XNAT,
# a link is created as a way of designating that file has been uploaded. Therefore, any files that do not have
# a link are yet to be uploaded and need actioning. Any files where the mtime is NEWER than the link's creation time
# need re-uploading (as they have obviously been updated since the last run).
# Note that this assumes that DICOM files are present for each archive. If not, then it will fail.
# Note this has the advantage that if you want to re-upload a file, just delete its link.
#
# So here's the step-by-step method
# 1. Search for PV files
# 2. For each PV file, look for its corresponding link.
# 2-a: If a link does not exist, file needs uploading.
# 2-a-1. Upload it to XNAT as a compressed folder.
# 2-a-2. XNAT will only ingest the DICOMs. Also upload the .PVDataset as a resource.
# 2-a-2. Create a link to mark it as updated.
# 2-b: If a link exists, but is older, it means the archive has been modified since last upload.
# 2-b-1. If the link exists, check the mtime.
# 2-b-2. If the mtime is older than archive, then the archive needs updating. Re-upload both the compressed archive
#        and the .PvDataset. TODO: figure out how XNAT handles this.
# 2-b-3. Create a new link to mark it as updated.

import pandas as pd
from pathlib import Path
import subprocess
import xnat

# Configuration
XNAT_DATA_DIR = '/data/test_projects'
XNAT_LINK_DIR = '/data/test_links'


# Useful methods
# Uploads an archive to XNAT (including PvDataset) and associates with a given project. Uploads will overwrite
# scans.
def upload_archive(archive, project):
    with xnat.connect('http://localhost') as session:
        # Upload (and ovewrite) the XNAT stored experiment
        exp = session.services.import_(
            path=str(archive), project=project, content_type="application/zip", overwrite="delete")
        # If it doesn't exist, create a PvDatasets resource
        if "PvDatasets" not in exp.resources.keys():
            session.classes.ResourceCatalog(parent=exp, label='PvDatasets')
        # Now upload the file (allow overwriting)
        exp.resources['PvDatasets'].upload(str(archive), archive.name, overwrite="delete")


# SCRIPT STARTS HERE
projects = [d.name for d in Path(XNAT_DATA_DIR).iterdir() if d.is_dir()]

# TODO: Fix to run on all projects, not just this test one
project = projects[0]
# Create the link dir if needed
project_link_dir = Path(f"{XNAT_LINK_DIR}/{project}")
if not project_link_dir.exists():
    try:
        project_link_dir.mkdir()
    except:
        print("Project link dir can't be created - exiting.")
        exit(1)  # Change to "next" when looping over projects


# Step 1: search for all PV files: search XNAT_DATA_DIR for .PvDatasets
archived_files = Path(f"{XNAT_DATA_DIR}/{project}").glob("**/*.PvDatasets")
for archive in archived_files:
    # Step 2: search for its corresponding link
    link = Path(f"{XNAT_LINK_DIR}/{project}/{archive.name}")
    if link.is_symlink():
        # Link already exists: check if the archive is newer (i.e. link out of date)
        if archive.stat().st_mtime > link.lstat().st_mtime:
            print("Archived modified: needs re-upload")
            upload_archive(archive, project)
            subprocess.run(["touch", "-h", f"{link}"])
        else:
            print("Link is up to date!")
    else:
        # Step 2-a, 2-a-1: link does not exist: upload to XNAT
        print(f"Link {link.name} doesn't exist - creating")
        print(f"archive is {str(archive)}")
        upload_archive(archive, project)
        link.symlink_to(archive)
