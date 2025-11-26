# find_daily_arise.py — locate daily ARISE-SAI data on AWS S3

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
        print("Path does not exist")
        return []


# === ROOT PATH FOR THIS SIMULATION ===
root = (
    "ncar-cesm2-arise/ARISE-SAI-1.5/"
    "b.e21.BW.f09_g17.SSP245-TSMLT-GAUSS-DEFAULT.001"
)

# ========================================================================
# 1. List all subfolders under atm/proc/tseries to reveal day_1, month_1, etc.
# ========================================================================

tseries_path = f"{root}/atm/proc/tseries"
print("STEP 1: Checking what exists inside tseries (daily, monthly, 6-hourly?)")
ts_items = ls(tseries_path)

# ========================================================================
# 2. If day_1 exists, show its contents
# ========================================================================

day_path = f"{tseries_path}/day_1"
if any("day_1" in x for x in ts_items):
    print("\nSTEP 2: DAILY data found! Listing files:")
    ls(day_path)
else:
    print("\nSTEP 2: No day_1 folder found under tseries. Checking hist files...")
    
    # ========================================================================
    # 3. If daily time-series do not exist, many CESM simulations store them in atm/hist
    # ========================================================================
    hist_path = f"{root}/atm/hist"
    hist_items = ls(hist_path)

    # Search for "h1" history files that are daily or sub-daily
    print("\nSTEP 3: Searching for 1-day (h1) CAM files inside atm/hist ...")

    h1_files = [f for f in hist_items if ".h1." in f]
    for f in h1_files[:20]:
        name = f.split("/")[-1]
        size = fs.du(f) / 1e9
        print(f"   📄 {name}  ({size:.3f} GB)")

    print(f"\nFound {len(h1_files)} h1 files (1-day or sub-daily CAM history).")
