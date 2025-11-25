# plot_arise_sargasso_scaling_PERFECT.py  ← THIS ONE IS BULLETPROOF
import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import glob
import os
import re
import cftime

folder = "ARISE_SST_files"

# ------------------------------------------------------------


def get_member(fn):
    m = re.search(r'\.(\d{3})\.cam', fn)
    return m.group(1) if m else "000"


# Load all files
sai_files = sorted(glob.glob(os.path.join(folder, "*DEFAULT*SST*.nc")))
ctrl_files = sorted(glob.glob(os.path.join(folder, "*WACCM*SST*.nc")))

ds_sai = xr.concat([xr.open_dataset(f).expand_dims(
    member=[f"S{get_member(f)}"]) for f in sai_files],  dim='member')
ds_ctrl = xr.concat([xr.open_dataset(f).expand_dims(
    member=[f"C{get_member(f)}"]) for f in ctrl_files], dim='member')

# ------------------------------------------------------------
# Sargasso Sea box
lat_min, lat_max = 20, 35
lon_min, lon_max = 300, 330   # 60°W–30°W

# CORRECT regional mean (area-weighted)


def regional_mean(da):
    # cosine latitude weights
    weights = np.cos(np.deg2rad(da.lat))
    da_reg = da.sel(lat=slice(lat_min, lat_max),
                    lon=slice(lon_min, lon_max))      # cut the box
    return da_reg.weighted(weights).mean(dim=['lat', 'lon'])


# Apply
real = regional_mean(ds_sai.SST - 273.15).mean('member')
ctrl = regional_mean(ds_ctrl.SST - 273.15).mean('member')
anomaly_real = real - ctrl

# Linear scaling
anomaly_3Tg = anomaly_real * (3.0 / 1.5)
anomaly_6Tg = anomaly_real * (6.0 / 1.5)

# ------------------------------------------------------------
# Convert time to decimal years (works with cftime)


def to_year_decimal(time_da):
    return np.array([t.year + (t.dayofyr - 1) / 365.0 for t in time_da.values])


time_y = to_year_decimal(anomaly_real.time)

# ------------------------------------------------------------
# Plot — beautiful and error-free
plt.figure(figsize=(15, 8))

plt.plot(time_y, anomaly_real, color='darkblue', lw=4,
         label='Real: 1.5 Tg SO₂/yr (10 members)')
plt.plot(time_y, anomaly_3Tg,  color='teal',
         lw=3.5, label='Scaled: 3.0 Tg SO₂/yr')
plt.plot(time_y, anomaly_6Tg,  color='crimson',
         lw=3.5, label='Scaled: 6.0 Tg SO₂/yr')

plt.axvspan(2035, 2055, color='gold', alpha=0.3, label='SAI injection period')
plt.axhline(0, color='black', lw=1.3)

plt.title('ARISE-SAI-1.5: Sargasso Sea SST Response + Linear Scaling\n'
          '20°–35°N, 60°–30°W', fontsize=19, pad=25)
plt.ylabel('ΔSST vs SSP2-4.5 Control (°C)', fontsize=16)
plt.xlabel('Year', fontsize=16)
plt.xlim(2015, 2070)
plt.ylim(-7, 5)
plt.grid(alpha=0.4, linestyle='--')
plt.legend(fontsize=15)
plt.tight_layout()
plt.show()

# ------------------------------------------------------------
print("\nSargasso Sea — Peak cooling (2040–2054):")
print(
    f"   1.5 Tg/yr (real)   : {float(anomaly_real.sel(time=slice('2040', '2054')).min()):.3f} °C")
print(
    f"   3.0 Tg/yr (scaled) : {float(anomaly_3Tg.sel(time=slice('2040', '2054')).min()):.3f} °C")
print(
    f"   6.0 Tg/yr (scaled) : {float(anomaly_6Tg.sel(time=slice('2040', '2054')).min()):.3f} °C")
print(
    f"Termination shock (2055–2060) — 6 Tg/yr scaled: +{float(anomaly_6Tg.sel(time=slice('2055', '2060')).max()):.3f} °C")
