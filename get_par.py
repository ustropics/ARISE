# get_par.py. (downloads PAR files)
import s3fs
from tqdm import tqdm
import os

fs = s3fs.S3FileSystem(anon=True)
os.makedirs("ARISE_PAR_files", exist_ok=True)

sai_files = fs.glob(
    "ncar-cesm2-arise/ARISE-SAI-1.5/*/atm/proc/tseries/month_1/*FSDS*.nc")
ctrl_files = fs.glob(
    "ncar-cesm2-arise/CESM2-WACCM-SSP245/*/atm/proc/tseries/month_1/*FSDS*.nc")

all_files = sai_files + ctrl_files
print(f"Found {len(all_files)} FSDS files → will compute PAR = FSDS × 0.43")

for remote_path in tqdm(all_files, desc="Downloading FSDS"):
    filename = remote_path.split("/")[-1]
    local_path = f"ARISE_PAR_files/{filename}"
    if not os.path.exists(local_path):
        fs.get(remote_path, local_path)

print("DONE! FSDS downloaded. Use ×0.43 to get real PAR.")
