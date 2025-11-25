# download_sss.py  ← Surface salinity for all members
import s3fs
from tqdm import tqdm
import os

fs = s3fs.S3FileSystem(anon=True)
os.makedirs("ARISE_SSS_files", exist_ok=True)

sai_files = fs.glob(
    "ncar-cesm2-arise/ARISE-SAI-1.5/*/ocn/proc/tseries/month_1/*SSS*.nc")
ctrl_files = fs.glob(
    "ncar-cesm2-arise/CESM2-WACCM-SSP245/*/ocn/proc/tseries/month_1/*SSS*.nc")

all_files = sai_files + ctrl_files
print(f"Found {len(all_files)} SSS files (20 total)")

for remote_path in tqdm(all_files, desc="Downloading SSS"):
    filename = remote_path.split("/")[-1]
    local_path = f"ARISE_SSS_files/{filename}"
    if not os.path.exists(local_path):
        fs.get(remote_path, local_path)

print("DONE! SSS files downloaded to ./ARISE_SSS_files/")
