#!/usr/bin/env python
# flake8: noqa

"""Downloads data from the USGS Watershed Boundary Dataset FTP into a local
   directory HUC_Data/"""

import os
import shutil
import urllib.request
import zipfile

HUC_SUBSETS = 22
OUT_DIR = "./HUC_Data/"
BASE_PATH = "ftp://rockyftp.cr.usgs.gov/vdelivery/Datasets/Staged/Hydrography/WBD/HU2/Shape/"

if os.path.exists(OUT_DIR):
    shutil.rmtree(OUT_DIR)

os.makedirs(OUT_DIR)

print("Downloading HUC data. This may take a while!")
for i in range(HUC_SUBSETS):
    print("Downloading {}/{}".format(i + 1, HUC_SUBSETS))
    zip_file, _ = urllib.request.urlretrieve(BASE_PATH +
                                             "WBD_{}_HU2_Shape.zip".format(str(i + 1).zfill(2)),
                                             OUT_DIR +
                                             "WBD_{}_HU2_Shape.zip".format(str(i + 1).zfill(2)))

    with zipfile.ZipFile(zip_file, "r") as f:
        f.extractall(OUT_DIR + "WBD_{}_HU2_Shape".format(str(i + 1).zfill(2)))

for item in os.listdir(OUT_DIR):
    if item.endswith(".zip"):
        os.remove(os.path.join(OUT_DIR, item))
