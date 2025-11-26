# plt_sst.py (plots sea surface temperatures)
import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import glob
import os
import re
import cftime

folder = "ARISE_SST_files"

# --------------------------------------------------------------
def get_member(fn):
    m = re.search(r'\.(\d{3})\.cam', fn)
    return m.group(1) if m else "000"


# Load exactly like before
sai_files = sorted(glob.glob(os.path.join(folder, "*DEFAULT*SST*.nc")))
ctrl_files = sorted(glob.glob(os.path.join(folder, "*WACCM*SST*.nc")))

ds_sai = xr.concat([xr.open_dataset(f).expand_dims(
    member=[f"S{get_member(f)}"]) for f in sai_files],  dim='member')
ds_ctrl = xr.concat([xr.open_dataset(f).expand_dims(
    member=[f"C{get_member(f)}"]) for f in ctrl_files], dim='member')

# --------------------------------------------------------------
# define lat/lon extension
lat_min, lat_max = 20, 35
lon_min, lon_max = 300, 330   # 60°W–30°W


# lat_min, lat_max = 20, 90      # Northern Hemisphere extratropics
# lon_min, lon_max = 0, 359

# lat_min, lat_max = -90, -60    # Southern Ocean / Antarctic
# lon_min, lon_max = 0, 359

# lat_min, lat_max = 5, -5       # Niño 3.4 region (needs correct lons below)
# lon_min, lon_max = 190, 240

# --------------------------------------------------------------
# Regional mean (area-weighted)


def regional_mean(da):
    weights = np.cos(np.deg2rad(da.lat))
    return da.sel(lat=slice(lat_min, lat_max), lon=slice(lon_min, lon_max)) \
             .weighted(weights).mean(['lat', 'lon'])


sai_reg = regional_mean(ds_sai.SST - 273.15).mean('member')
ctrl_reg = regional_mean(ds_ctrl.SST - 273.15).mean('member')
anomaly_reg = sai_reg - ctrl_reg

# --------------------------------------------------------------
# Plot
t1 = cftime.DatetimeNoLeap(2035, 1, 1)
t2 = cftime.DatetimeNoLeap(2055, 1, 1)

plt.figure(figsize=(16, 10))
anomaly_reg.plot(color='darkblue', linewidth=3.5,
                 label='ARISE-SAI-1.5 (10-member mean)')

plt.axvspan(t1, t2, color='gold', alpha=0.3,
            label='SAI injection (1.5 Tg SO₂/yr)')
plt.axhline(0, color='black', lw=1.2)

region_name = f"Sargasso Sea ({lat_min}°–{lat_max}° lat, {lon_min}°–{lon_max}° lon)"

plt.title(f'ARISE-SAI-1.5: Regional Sea Surface Temperature Anomaly (SSTA)\n{region_name}',
          fontsize=18, pad=20)
plt.ylabel('SST Delta (°C)', fontsize=16)
plt.xlabel('Year', fontsize=16)
plt.xlim(cftime.DatetimeNoLeap(2015, 1, 1), cftime.DatetimeNoLeap(2070, 1, 1))
plt.ylim(anomaly_reg.min()-0.2, anomaly_reg.max()+0.4)
plt.grid(alpha=0.35)
plt.legend(fontsize=15)
plt.tight_layout()
plt.show()

# Print numbers for your chosen region
print(
    f"\nRegion: {lat_min}° to {lat_max}° latitude, {lon_min}° to {lon_max}° longitude")
print(
    f"Peak cooling (2040–2054): {float(anomaly_reg.sel(time=slice('2040', '2054')).min()):.3f} °C")
print(
    f"Termination shock (2055–2060): +{float(anomaly_reg.sel(time=slice('2055', '2060')).max()):.3f} °C")
