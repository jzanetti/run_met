# run_met

# Synopsis
Collect the necessary wrf inputs and observations and run MET based verifications

# Directories structure
## forecast preprocessing
```
    * fcst/2017121801/wrf_hourly_*                    : downloaded wrf output 
                                                       ("2017121801 is the analysis time")
    * wrf_interp/2017121801/wrf_hourly_*              : wrf output from wrf_interp
                                                       ("2017121801 is the analysis time")
```
                      
## observation preprocessing
```
    * little_r/all.little_r.2017121802                : downloaded observation (in little_r)
    * obsproc/obs_gts_2017-12-18_02:00:00.3DVAR       : obs processed by obsproc (hourly data)
    * obs_ascii/obs_ascii                             : obs written in ascii for MET
    * ascii2nc/obs_ascii.nc                           : obs written in netcdf
```

## MET: verification
```
     * met_dir/point_stat/2017121801/*                : output from point_stat
                                                        ("2017121801 is the analysis time")
```

# Workflow
1. Run `--download_obs` and `download_fcst` to download the required observations and forecasts
2. Run `--run_obspreprocess` to preprocess the observations, it combines three steps:
    2.1. `--run_obsproc`: run obsproc
    2.2. `--run_obs2ascii`: convert the output from `run_obsproc` to ascii format
    2.3. `--run_ascii2nc`: convert the output from `run_obs2ascii` to netcdf
3. Run `--run_wrf_interp` to preprocess the forecasts
4. Run any MET applications
