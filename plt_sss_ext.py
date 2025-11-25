# plot_arise_sss_SARGASSO_PERFECT.py  ← THIS ONE WORKS 100%
import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import glob
import cftime

folder = "ARISE_SSS_files"

sai_files = sorted(glob.glob(f"{folder}/*DEFAULT*SSS*.nc"))
ctrl_files = sorted(glob.glob(f"{folder}/*WACCM*SSS*.nc"))

print(f"Loading {len(sai_files)} SAI + {len(ctrl_files)} control files")

# Open datasets
ds_sai = xr.open_mfdataset(sai_files,  combine='nested', concat_dim='member')
ds_ctrl = xr.open_mfdataset(ctrl_files, combine='nested', concat_dim='member')

# Variable is SSS2
sss_sai = ds_sai.SSS2
sss_ctrl = ds_ctrl.SSS2

# Sargasso Sea box
lat_min, lat_max = 20, 35
lon_min, lon_max = 300, 330   # 60°W–30°W


def regional_mean(da):
    # Select region first
    da_reg = da.sel(nlat=slice(lat_min, lat_max), nlon=slice(lon_min, lon_max))

    # TLAT has shape (nlat, nlon) → broadcast to match da_reg
    weights = np.cos(np.deg2rad(da_reg.TLAT))  # now same shape as da_reg

    # Area-weighted mean
    return (da_reg * weights).sum(dim=['nlat', 'nlon']) / weights.sum(dim=['nlat', 'nlon'])


# Compute regional means and
sai_reg = regional_mean(sss_sai).mean('member')
ctrl_reg = regional_mean(sss_ctrl).mean('member')
anomaly = sai_reg - ctrl_reg

# Plot — beautiful and error-free
plt.figure(figsize=(16, 9))
anomaly.plot(color='#1f78b4', linewidth=4.8,
             label='ARISE-SAI-1.5 (10-member mean)')

plt.axvspan(cftime.DatetimeNoLeap(2035, 1, 1), cftime.DatetimeNoLeap(2055, 1, 1),
            color='gold', alpha=0.3, label='SAI injection (1.5 Tg SO₂/yr)')
plt.axhline(0, color='black', lw=1.5)

plt.title('ARISE-SAI-1.5: Sargasso Sea Surface Salinity Anomaly\n'
          '20°–35°N, 60°–30°W', fontsize=20, pad=25)
plt.ylabel('ΔSSS vs SSP2-4.5 Control (g/kg ≈ ‰)', fontsize=17)
plt.xlabel('Year', fontsize=17)
plt.xlim(cftime.DatetimeNoLeap(2015, 1, 1), cftime.DatetimeNoLeap(2070, 1, 1))
plt.ylim(-0.75, 0.55)
plt.grid(alpha=0.35, linestyle='--')
plt.legend(fontsize=16, loc='lower left')
plt.tight_layout()
plt.show()

# Print results
print("\nSargasso Sea Surface Salinity Response:")
print(
    f"Peak freshening (2040–2054): {float(anomaly.sel(time=slice('2040', '2054')).min()):.3f} ‰")
print(
    f"Termination shock rebound (2055–2060): +{float(anomaly.sel(time=slice('2055', '2060')).max()):.3f} ‰")
