# download_sst_only.py
import s3fs
from tqdm import tqdm
import os

fs = s3fs.S3FileSystem(anon=True)
os.makedirs("ARISE_SST_files", exist_ok=True)

sai_files = fs.glob(
    "ncar-cesm2-arise/ARISE-SAI-1.5/*/atm/proc/tseries/month_1/*SST*.nc")
ctrl_files = fs.glob(
    "ncar-cesm2-arise/CESM2-WACCM-SSP245/*/atm/proc/tseries/month_1/*SST*.nc")

all_files = sai_files + ctrl_files
print(f"Downloading {len(all_files)} SST files (total ~30–40 GB max)...")

for remote_path in tqdm(all_files, desc="Downloading"):
    filename = remote_path.split("/")[-1]
    local_path = f"ARISE_SST_files/{filename}"
    if not os.path.exists(local_path):
        fs.get(remote_path, local_path)
    else:
        print(f"   Already have {filename}")

print("DONE! All SST files are now in ./ARISE_SST_files/")
