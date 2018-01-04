# run_met

# Synopsis
Collect the necessary wrf inputs and observations (ADPSFC) and run MET based verifications

# Scripts:
1. start_met.py: run the basic met verification for single model
2. start_multiple_met.py: run multiple models by called start_met.py multiple times
3. start_plot.py: plot the met outputs

# start_met.py
## Directories structure
### forecast preprocessing
```
    * fcst/2017121801/wrf_hourly_*                    : downloaded wrf output 
                                                       ("2017121801 is the analysis time")
    * wrf_interp/2017121801/wrf_hourly_*              : wrf output from wrf_interp
                                                       ("2017121801 is the analysis time")
```
                      
### observation preprocessing
```
    * little_r/all.little_r.2017121802                : downloaded observation (in little_r)
    * obsproc/obs_gts_2017-12-18_02:00:00.3DVAR       : obs processed by obsproc (hourly data)
    * obs_ascii/obs_ascii                             : obs written in ascii for MET
    * ascii2nc/obs_ascii.nc                           : obs written in netcdf
```

### MET: verification
```
     * met_dir/point_stat/2017121801/*                : output from point_stat
                                                        ("2017121801 is the analysis time")
```

### Workflow
1. Run `--download_obs` and `download_fcst` to download the required observations and forecasts
``` Note: this step must be run in AWS```
2. Run `--run_obspreprocess` to preprocess the observations, it combines three steps:
    2.1. `--run_obsproc`: run obsproc
    2.2. `--run_obs2ascii`: convert the output from `run_obsproc` to ascii format
    2.3. `--run_ascii2nc`: convert the output from `run_obs2ascii` to netcdf
3. Run `--run_wrf_interp` to preprocess the forecasts
4. Run any MET applications

### Sample run command for start_met.py
```
export model=nz8kmN-NCEP-var
export domain_id=2
export download_fcst_source=s3://metservice-research-us-west-2/research/archive-data/wrf_archive/wrfout
export ascii2nc_config=/opt/miniconda2/envs/met/lib/python2.7/site-packages/run_met/../../../../run_met/etc/ascii2nc.config
export pointstat_config=/opt/miniconda2/envs/met/lib/python2.7/site-packages/run_met/../../../../run_met/etc/pointstat.config
export work_dir=/mnt/WRF/met
export obsproc_installation=/opt/miniconda2/envs/met/wrfda/WRFDA/var/obsproc
export wrf_interp_installation=/opt/miniconda2/envs/met/wrf_interp
export met_installation=/opt/miniconda2/envs/met/met

start_met.py --start_analysis 201712180100 --end_analysis 201712180200 --forecast_length 1 --analysis_time_interval 1 --new_run --obsproc_installation $obsproc_installation --wrf_interp_installation $wrf_interp_installation --met_installation $met_installation --work_dir $work_dir --model $model --domain_id $domain_id --download_obs --download_fcst --run_obspreprocess --run_wrf_interp --run_pointstat --ascii2nc_config $ascii2nc_config --download_fcst_source $download_fcst_source --pointstat_config $pointstat_config
```

# start_multiple_met.py
You need to edit the script start_multiple_met.py directly to control the multi models verifications
Location of ```start_multiple_met.py```
```
/opt/miniconda2/envs/met/bin/start_multiple_met.py
```

# start_plot.py
## Sample run command for start_plot.py
```
start_plot.py --start_analysis_time 201712250000 --end_analysis_time 201712250000 --forecast_length 6 --analysis_time_interval 1 --model_list nz8kmN-NCEP nz8kmN-NCEP-obsnudge --met_task point_stat --met_out_dir /home/szhang/Desktop/run_ver/met --plot_field_list T2
```


# Contributor:
Sijin Zhang
