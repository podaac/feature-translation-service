#!/usr/bin/env python
# flake8: noqa

"""Downloads data from the USGS Watershed Boundary Dataset FTP into a local
   directory HUC_Data/"""

import os
import shutil
import zipfile

import requests

HUC_SUBSETS = 22
OUT_DIR = "./HUC_Data/"
BASE_PATH = "https://prd-tnm.s3.amazonaws.com/StagedProducts/Hydrography/WBD/HU2/Shape/"

if os.path.exists(OUT_DIR):
    shutil.rmtree(OUT_DIR)

os.makedirs(OUT_DIR)

print("Downloading HUC data. This may take a while!")
for i in range(HUC_SUBSETS):
    print(f"Downloading {i + 1}/{HUC_SUBSETS}")
    zip_name = f"WBD_{str(i + 1).zfill(2)}_HU2_Shape.zip"
    zip_file = OUT_DIR + zip_name
    url = BASE_PATH + zip_name
    response = requests.get(url, stream=True, timeout=30)
    if response.status_code == 200:
        with open(zip_file, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
    print(f"zip_file: {zip_file}")

    with zipfile.ZipFile(zip_file, "r") as f:
        f.extractall(OUT_DIR + f"WBD_{str(i + 1).zfill(2)}_HU2_Shape")

for item in os.listdir(OUT_DIR):
    if item.endswith(".zip"):
        os.remove(os.path.join(OUT_DIR, item))
