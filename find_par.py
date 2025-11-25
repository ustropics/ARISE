# arise_find_variables.py  ← THIS WILL TELL US THE TRUTH ABOUT PAR
import s3fs
fs = s3fs.S3FileSystem(anon=True)


def ls(path, n=30):
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


# Known good path — this is where the monthly time-series live
path = "ncar-cesm2-arise/ARISE-SAI-1.5/b.e21.BW.f09_g17.SSP245-TSMLT-GAUSS-DEFAULT.001/atm/proc/tseries/month_1"

print("STEP 1: Inside the monthly time-series folder (where SST, TS, etc. live)")
ls(path)

print("\nSTEP 2: Let's search for anything with 'PAR', 'PHOTO', or 'RAD' in the name")
all_files = fs.glob(path + "/*.nc")
matching = [f for f in all_files if any(keyword in f.upper() for keyword in [
                                        "PAR", "PHOTO", "RAD", "SW", "FLNS", "FSNS"])]
for f in matching[:20]:
    name = f.split("/")[-1]
    size = fs.du(f) / 1e9
    print(f"   📄 {name}  → {size:.3f} GB")

print(f"\nTotal monthly time-series files: {len(all_files)}")
