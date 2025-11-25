# plot_arise_global_sst_map.py  ← SPATIAL ANOMALY MAP
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
import glob
import os
import re

folder = "ARISE_SST_files"


def get_member(fn):
    m = re.search(r'\.(\d{3})\.cam', fn)
    return m.group(1) if m else "000"


# Load all SST files
sai_files = sorted(glob.glob(os.path.join(folder, "*DEFAULT*SST*.nc")))
ctrl_files = sorted(glob.glob(os.path.join(folder, "*WACCM*SST*.nc")))

# Open and add member dimension
ds_sai = xr.concat([xr.open_dataset(f).expand_dims(
    member=[f"S{get_member(f)}"]) for f in sai_files],  dim='member')
ds_ctrl = xr.concat([xr.open_dataset(f).expand_dims(
    member=[f"C{get_member(f)}"]) for f in ctrl_files], dim='member')

# Convert to °C
sst_sai = ds_sai.SST - 273.15
sst_ctrl = ds_ctrl.SST - 273.15

# Compute 2040–2054 average (peak cooling period)
sai_peak = sst_sai.sel(time=slice('2040', '2054')).mean(['time', 'member'])
ctrl_peak = sst_ctrl.sel(time=slice('2015', '2069')).mean(['time', 'member'])
anomaly_map = sai_peak - ctrl_peak

anomaly_map = anomaly_map * (3.0 / 1.5)

# Plot
fig = plt.figure(figsize=(16, 9))
ax = plt.axes(projection=ccrs.Robinson())
ax.set_global()

# Plot the anomaly
im = anomaly_map.plot.contourf(
    ax=ax, transform=ccrs.PlateCarree(),
    levels=np.linspace(-1.5, 1.5, 101),
    cmap='RdBu_r',
    extend='both',
    add_colorbar=False
)

# Add coastlines and land (gray)
ax.coastlines(resolution='110m', linewidth=0.8)
ax.add_feature(cfeature.LAND, facecolor='lightgray', zorder=2)
ax.add_feature(cfeature.BORDERS, linewidth=0.5, edgecolor='gray')

# Colorbar
cbar = plt.colorbar(im, ax=ax, orientation='horizontal', pad=0.05, shrink=0.7)
cbar.set_label(
    'SST Anomaly vs SSP2-4.5 Control (°C) — 2040–2054 mean', fontsize=14)
cbar.ax.tick_params(labelsize=12)

# Title
plt.title('ARISE-SAI-1.5 (1.5 Tg SO₂/yr): Peak Cooling Period SST Response\n'
          'Ensemble Mean (10 members), 2040–2054 average',
          fontsize=18, pad=20)

plt.tight_layout()
plt.show()

# Print global mean cooling
global_cooling = anomaly_map.weighted(
    np.cos(np.deg2rad(anomaly_map.lat))).mean().values
print(f"Global mean SST cooling (2040–2054): {global_cooling:.3f} °C")
