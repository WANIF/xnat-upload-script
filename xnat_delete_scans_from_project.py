#!/usr/bin/python3

# Script to delete all scans from a given project. USE WITH CAUTION.
# Useful when re-uploading everything following catastrophic configuration
# error.

# Run using the following syntax: $ xnat_delete_scans_from_project.py projectname

# Needs a username/password ~/.netrc to connect, with permission 600, with the following syntax:

# machine xnat-mri.cmca.uwa.edu.au
#         login admin
#         password <password>
#

import sys
import xnat

# Exit if usage is incorrect
if len(sys.argv) != 2:
    print("Usage: $ xnat_delete_scans_from_project.py projectname")
    exit(1)
project_name = sys.argv[1]

with xnat.connect('https://xnat-mri.cmca.uwa.edu.au') as session:

    try:
        project = session.projects[project_name]
    except Exception as e:
        print(f"Unable to find project {project_name}: {str(e)}\n")
        exit(2)

    try:
        subjects = project.subjects
    except Exception as e:
        print(f"Unable to find subjects with unknown error: {str(e)}\n")
        exit(3)

    if len(subjects) < 1:
        print(f"No subjects found in project {project_name}\n")
        exit(0)

    # If all is good, delete every subject
    for subj in subjects.values():
        try:
            print(f"Deleting {str(subj.label)}...\n")
            subj.delete(remove_files=True)
        except Exception as e:
            print(f"Subject {str(subj)} unable to be deleted: {str(e)}\n")


print("Deletions complete!\n")
exit(0)

