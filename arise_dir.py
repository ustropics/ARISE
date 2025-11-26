# arise_dir.py (find files on AWS bucket)
import s3fs
fs = s3fs.S3FileSystem(anon=True)


def ls(path, n=20):
    print(f"\n=== {path} ===")
    try:
        items = fs.ls(path, detail=False)
        for i, item in enumerate(items[:n]):
            name = item.split("/")[-1]
            if fs.isdir(item):
                print(f"   📁 {name}/")
            else:
                size_gb = fs.du(item) / 1e9
                print(f"   📄 {name}  ({size_gb:.3f} GB)")
        if len(items) > n:
            print(f"   ... and {len(items) - n} more items")
        return items
    except FileNotFoundError:
        print("   ❌ Path does not exist")
        return []


# Start with one known real member from each ensemble
sai_member = "ncar-cesm2-arise/ARISE-SAI-1.5/b.e21.BW.f09_g17.SSP245-TSMLT-GAUSS-DEFAULT.001"
ctrl_member = "ncar-cesm2-arise/CESM2-WACCM-SSP245/b.e21.BWSSP245cmip6.f09_g17.CMIP6-SSP2-4.5-WACCM.001"

print("STEP 1: Root of SAI member 001")
ls(sai_member)

print("\nSTEP 2: Root of Control member 001")
ls(ctrl_member)

print("\nSTEP 3: Inside SAI atm/")
ls(sai_member + "/atm")

print("\nSTEP 4: Inside SAI atm/proc/")
ls(sai_member + "/atm/proc")

print("\nSTEP 5: Inside Control atm/proc/")
ls(ctrl_member + "/atm/proc")

print("\nSTEP 6: Inside SAI ocn/proc/ (for real ocean SST)")
ls(sai_member + "/ocn/proc")

print("\nSTEP 7: First 10 actual .nc files in SAI atm/proc/")
files = fs.glob(sai_member + "/atm/proc/*.nc")
for f in files[:10]:
    size = fs.du(f) / 1e9
    print(f"   {f.split('/')[-1]}  → {size:.3f} GB")
