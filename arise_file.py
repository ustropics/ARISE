# arise_file.py (shows meta data for files on local)
import s3fs
fs = s3fs.S3FileSystem(anon=True)

# SAI member 001 – atmosphere monthly time series
path_sai = "ncar-cesm2-arise/ARISE-SAI-1.5/b.e21.BW.f09_g17.SSP245-TSMLT-GAUSS-DEFAULT.001/atm/proc/tseries/month_1"

print("SAI atmosphere monthly files (first 15):")
files = fs.ls(path_sai)
for f in files[:15]:
    size = fs.du(f) / 1e9
    print(f"   {f.split('/')[-1]:70}  {size:6.3f} GB")

# Control member 001 – same structure
path_ctrl = "ncar-cesm2-arise/CESM2-WACCM-SSP245/b.e21.BWSSP245cmip6.f09_g17.CMIP6-SSP2-4.5-WACCM.001/atm/proc/tseries/month_1"

print("\nControl atmosphere monthly files (first 10):")
files = fs.ls(path_ctrl)[:10]
for f in files:
    size = fs.du(f) / 1e9
    print(f"   {f.split('/')[-1]:70}  {size:6.3f} GB")
