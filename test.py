# arise_sst_DONE.py  ← RUN THIS AND YOU WIN
import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import s3fs

fs = s3fs.S3FileSystem(anon=True)

# Global mean helper


def gm(da):
    w = np.cos(np.deg2rad(da.lat))
    return da.weighted(w).mean(['lat', 'lon'])


# ------------------ SAI (10 members) ------------------
sai_files = fs.glob(
    "ncar-cesm2-arise/ARISE-SAI-1.5/*/atm/proc/tseries/month_1/*SST*.nc"
)
print(f"SAI SST files: {len(sai_files)}")

ds_sai = xr.open_mfdataset([fs.open(f) for f in sai_files],
                           combine='by_coords', parallel=True)
sai_sst = gm(ds_sai.SST - 273.15).compute()

# ------------------ Control (10 members) ------------------
ctrl_files = fs.glob(
    "ncar-cesm2-arise/CESM2-WACCM-SSP245/*/atm/proc/tseries/month_1/*SST*.nc"
)
print(f"Control SST files: {len(ctrl_files)}")

ds_ctrl = xr.open_mfdataset([fs.open(f) for f in ctrl_files],
                            combine='by_coords', parallel=True)
ctrl_sst = gm(ds_ctrl.SST - 273.15).mean('member').compute()

# ------------------ Plot ------------------
plt.figure(figsize=(13, 6))
anomaly = sai_sst - ctrl_sst

plt.plot(anomaly.time, anomaly, color='darkblue', linewidth=3,
         label='ARISE-SAI-1.5 ensemble mean (10 members)')

plt.axvspan('2035-01-01', '2055-01-01', color='gold', alpha=0.3,
            label='SAI injection (1.5 Tg SO₂/yr)')

plt.axhline(0, color='black', linewidth=1)
plt.title('ARISE-SAI-1.5: Global-Mean Sea Surface Temperature Response', fontsize=16)
plt.ylabel('SST Anomaly vs SSP2-4.5 Control (°C)', fontsize=14)
plt.xlim('2015', '2070')
plt.ylim(-1.6, 1.2)
plt.grid(alpha=0.3)
plt.legend(fontsize=12)
plt.tight_layout()
plt.show()

# Print the numbers everyone cites
print(
    f"Peak cooling (2040–2054): {float(anomaly.sel(time=slice('2040', '2054')).min()):.3f} °C")
print(
    f"Termination shock peak (2055–2060): +{float(anomaly.sel(time=slice('2055', '2060')).max()):.3f} °C")
