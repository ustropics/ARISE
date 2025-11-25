# plot_arise_par_global_CORRECT.py
import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import glob
import os
import re

folder = "ARISE_PAR_files"


def get_member(fn):
    m = re.search(r'\.(\d{3})\.cam', fn)
    return m.group(1) if m else "000"


# Load FSDS files
sai_files = sorted(glob.glob(os.path.join(folder, "*DEFAULT*FSDS*.nc")))
ctrl_files = sorted(glob.glob(os.path.join(folder, "*WACCM*FSDS*.nc")))

ds_sai = xr.concat([xr.open_dataset(f).expand_dims(
    member=[f"S{get_member(f)}"]) for f in sai_files],  dim='member')
ds_ctrl = xr.concat([xr.open_dataset(f).expand_dims(
    member=[f"C{get_member(f)}"]) for f in ctrl_files], dim='member')

# Compute PAR = FSDS × 0.43
par_sai = ds_sai.FSDS * 0.43
par_ctrl = ds_ctrl.FSDS * 0.43

# Global cosine-weighted mean


def gm(da):
    w = np.cos(np.deg2rad(da.lat))
    return da.weighted(w).mean(['lat', 'lon'])


par_sai_gm = gm(par_sai).mean('member')
par_ctrl_gm = gm(par_ctrl).mean('member')
anomaly = par_sai_gm - par_ctrl_gm

# Time → decimal years


def to_year(t):
    return np.array([t.year + (t.dayofyr-1)/365.0 for t in t.values])


time_y = to_year(anomaly.time)

# Plot
plt.figure(figsize=(16, 10))
plt.plot(time_y, anomaly, color="#e79b0d", lw=2,
         label='ARISE-SAI-1.5 PAR (10-member mean)')

plt.axvspan(2035, 2055, color='gold', alpha=0.3,
            label='SAI injection (1.5 Tg SO₂/yr)')
plt.axhline(0, color='black', lw=1.3)

plt.title('ARISE-SAI-1.5: Global Mean Photosynthetically Available Radiation (PAR)',
          fontsize=18, pad=20)
plt.ylabel('PAR Delta (W/m²)', fontsize=16)
plt.xlabel('Year', fontsize=16)
plt.xlim(2015, 2070)
plt.ylim(-5, 5)
plt.grid(alpha=0.4, linestyle='--')
plt.legend(fontsize=15)
plt.tight_layout()
plt.show()

print(
    f"Peak PAR reduction (2040–2054): {anomaly.sel(time=slice('2040', '2054')).min().values:.2f} W/m²")
print(
    f"Termination rebound (2055–2060): +{anomaly.sel(time=slice('2055', '2060')).max().values:.2f} W/m²")
