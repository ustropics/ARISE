# plot_arise_par_REGIONAL.py  ← NEW REGIONAL VERSION
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

sai_files = sorted(glob.glob(os.path.join(folder, "*DEFAULT*FSDS*.nc")))
ctrl_files = sorted(glob.glob(os.path.join(folder, "*WACCM*FSDS*.nc")))

ds_sai = xr.concat([xr.open_dataset(f).expand_dims(
    member=[f"S{get_member(f)}"]) for f in sai_files], dim='member')
ds_ctrl = xr.concat([xr.open_dataset(f).expand_dims(
    member=[f"C{get_member(f)}"]) for f in ctrl_files], dim='member')

# Compute PAR = FSDS × 0.43
par_sai = ds_sai.FSDS * 0.43
par_ctrl = ds_ctrl.FSDS * 0.43


# ===========================================================
lat_min, lat_max = 20, 35
lon_min, lon_max = 300, 330 

# Some popular boxes — comment/uncomment as needed:
# lat_min, lat_max = 20, 90       # NH extratropics
# lat_min, lat_max = -90, -20     # SH mid–high latitudes
# lat_min, lat_max = -90, 90      # Global (default if you want to keep it)
# lon_min, lon_max = 30, 150     # e.g., Indian Ocean sector, etc.
# ===========================================================


# Regional cosine-weighted mean
def regional_mean(da):
    weights = np.cos(np.deg2rad(da.lat))
    return da.sel(lat=slice(lat_min, lat_max), lon=slice(lon_min, lon_max)) \
             .weighted(weights).mean(['lat', 'lon'])


par_sai_reg = regional_mean(par_sai).mean('member')
par_ctrl_reg = regional_mean(par_ctrl).mean('member')
anomaly = par_sai_reg - par_ctrl_reg

def to_year(t):
    return np.array([t.year + (t.dayofyr - 1) / 365.0 for t in t.values])

time_y = to_year(anomaly.time)

plt.figure(figsize=(16, 10))
plt.plot(time_y, anomaly, color="#e79b0d", lw=3,
         label='ARISE-SAI-1.5 PAR (10-member mean)')

plt.axvspan(2035, 2055, color='gold', alpha=0.3,
            label='SAI injection (1.5 Tg SO₂/yr)')
plt.axhline(0, color='black', lw=1.3)

if lat_min == -90 and lat_max == 90 and lon_min == 0 and lon_max == 359:
    region_name = "Global"
else:
    region_name = f"Sargasso Sea ({lat_min}°–{lat_max}° lat, {lon_min}°–{lon_max}° lon)"

plt.title(f'ARISE-SAI-1.5: Regional Mean Photosynthetically Available Radiation (PAR)\n{region_name}',
          fontsize=18, pad=20)
plt.ylabel('PAR Anomaly (W/m²)', fontsize=16)
plt.xlabel('Year', fontsize=16)
plt.xlim(2015, 2070)
plt.ylim(anomaly.min() - 0.5, anomaly.max() + 0.5) 
plt.grid(alpha=0.4, linestyle='--')
plt.legend(fontsize=15)
plt.tight_layout()
plt.show()

print(
    f"\nRegion: {lat_min}° to {lat_max}° latitude, {lon_min}° to {lon_max}° longitude")
print(
    f"Peak PAR reduction (2040–2054): {anomaly.sel(time=slice('2040', '2054')).min().values:.2f} W/m²")
print(
    f"Termination rebound (2055–2060): +{anomaly.sel(time=slice('2055', '2060')).max().values:.2f} W/m²")
