# plot_arise_sst_FINAL_WORKING.py   ← COPY-PASTE & RUN
import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import glob
import os
import re
import cftime   # ← this is the key import

folder = "ARISE_SST_files"

# --------------------------------------------------------------


def get_member(fn):
    m = re.search(r'\.(\d{3})\.cam', fn)
    return m.group(1) if m else "000"


# --------------------------------------------------------------
# SAI ensemble (10 files)
sai_files = sorted(glob.glob(os.path.join(folder, "*DEFAULT*SST*.nc")))
ds_sai_list = [xr.open_dataset(f).expand_dims(
    member=[f"S{get_member(f)}"]) for f in sai_files]
ds_sai = xr.concat(ds_sai_list, dim='member')

# Control ensemble (20 files → 10 members)
ctrl_files = sorted(glob.glob(os.path.join(folder, "*WACCM*SST*.nc")))
ds_ctrl_list = [xr.open_dataset(f).expand_dims(
    member=[f"C{get_member(f)}"]) for f in ctrl_files]
ds_ctrl = xr.concat(ds_ctrl_list, dim='member')

# --------------------------------------------------------------
# Global mean


def gm(da):
    w = np.cos(np.deg2rad(da.lat))
    return da.weighted(w).mean(['lat', 'lon'])


sai_gm = gm(ds_sai.SST - 273.15).mean('member')
ctrl_gm = gm(ds_ctrl.SST - 273.15).mean('member')
anomaly = sai_gm - ctrl_gm

# --------------------------------------------------------------
# Plot – use cftime.DatetimeNoLeap (the calendar used in ARISE)
t1 = cftime.DatetimeNoLeap(2035, 1, 1)
t2 = cftime.DatetimeNoLeap(2055, 1, 1)

plt.figure(figsize=(14, 7))
anomaly.plot(color='darkblue', linewidth=3.5,
             label='ARISE-SAI-1.5 (10-member mean)')

plt.axvspan(t1, t2, color='gold', alpha=0.3,
            label='SAI injection (1.5 Tg SO₂/yr)')

plt.axhline(0, color='black', lw=1.2)
plt.title('ARISE-SAI-1.5: Global Mean Sea Surface Temperature Anomaly\n'
          'vs SSP2-4.5 Control Ensemble', fontsize=17, pad=20)
plt.ylabel('ΔSST (°C)', fontsize=14)
plt.xlabel('Year', fontsize=14)
plt.xlim(cftime.DatetimeNoLeap(2015, 1, 1), cftime.DatetimeNoLeap(2070, 1, 1))
plt.ylim(-1.6, 1.4)
plt.grid(alpha=0.35)
plt.legend(fontsize=14)
plt.tight_layout()
plt.show()

# --------------------------------------------------------------
print(
    f"Peak cooling (2040–2054): {float(anomaly.sel(time=slice('2040', '2054')).min()):.3f} °C")
print(
    f"Termination shock (2055–2060): +{float(anomaly.sel(time=slice('2055', '2060')).max()):.3f} °C")
