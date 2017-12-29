
import argparse
from datetime import datetime
import os
import shutil

import fcst_processing, obs_processing, met_processing


"""
    run_met directories structure
   ---------------------------------------
   - forecast preprocessing
   ---------------------------------------
    * fcst/2017121801/wrf_hourly_*                    : downloaded wrf output 
                                                       ("2017121801 is the analysis time")
    * wrf_interp/2017121801/wrf_hourly_*              : wrf output from wrf_interp
                                                       ("2017121801 is the analysis time")

   ---------------------------------------                          
   - observation preprocessing
   ---------------------------------------
    * little_r/all.little_r.2017121802                : downloaded observation (in little_r)
    * obsproc/obs_gts_2017-12-18_02:00:00.3DVAR       : obs processed by obsproc (hourly data)
    * obs_ascii/obs_ascii                             : obs written in ascii for MET
    * ascii2nc/obs_ascii.nc                           : obs written in netcdf
    
    ---------------------------------------
    - met: verification
    ---------------------------------------
     * met_dir/point_stat/2017121801/*                : output from point_stat
                                                        ("2017121801 is the analysis time")
                                                        
    ---------------------------------------
    - Example for debugging
    ---------------------------------------
        return PARSER.parse_args(['--start_analysis_time', '201712271800', '--end_analysis_time', '201712271800',
                              '--analysis_time_interval', '1', '--forecast_length', '2',
                              '--obsproc_installation', '/home/jzanetti/programs/WRFDA_V3.9.1/WRFDA/var/obsproc',
                              '--wrf_interp_installation', '/home/jzanetti/programs/wrf_interp/wrf_interp',
                              '--met_installation', '/home/jzanetti/programs/met-6.0.20170403/met-6.0',
                              '--work_dir', '//home/jzanetti/mydata/run_met',
                              '--run_obspreprocess', '--ascii2nc_config', '/home/jzanetti/workspace/run_met/etc/ascii2nc.config',
                              '--run_wrf_interp', '--model', 'nz8kmN-NCEP', '--domain_id', '2',
                              '--run_pointstat', '--pointstat_config', '/home/jzanetti/workspace/run_met/etc/pointstat.config'
                              ])

"""

def valid_datetime(timestamp):
    '''turn a timestamp into a datetime object'''
    try:
        return datetime.strptime(timestamp, "%Y%m%d%H%M")
    except ValueError:
        msg = "Not a valid date: '{}'.".format(timestamp)
    raise argparse.ArgumentTypeError(msg)

def setup_dir(new_run, working_dir):
    if new_run:
        if os.path.exists(working_dir):
            shutil.rmtree(working_dir)
    
    dir_dict = {}
    dir_dict['little_r_dir'] = os.path.join(working_dir, 'little_r')
    dir_dict['obsproc_dir'] = os.path.join(working_dir, 'obsproc')
    dir_dict['obs_ascii_dir'] = os.path.join(working_dir, 'obs_ascii')
    dir_dict['obs_ascii2nc'] = os.path.join(working_dir, 'ascii2nc')
    dir_dict['fcst_dir'] = os.path.join(working_dir, 'fcst')
    dir_dict['wrf_interp_dir'] = os.path.join(working_dir, 'wrf_interp')
    dir_dict['point_stat_dir'] = os.path.join(working_dir, 'met_dir', 'point_stat')
    
    for cdir in dir_dict.keys():
        if not os.path.exists(dir_dict[cdir]):
            os.makedirs(dir_dict[cdir])

    return dir_dict

def setup_parser():
    """run verifications"""
    PARSER = argparse.ArgumentParser(
            description='run verifications')
    
    # -----------------
    # required
    # -----------------
    PARSER.add_argument('--start_analysis_time', type=valid_datetime, 
                        required=True, help="start analysis time (YYYYMMDDHHM)")
    PARSER.add_argument('--end_analysis_time', type=valid_datetime, 
                        required=True, help="end analysis time (YYYYMMDDHHM)")
    PARSER.add_argument('--forecast_length', type=str, 
                        required=True, help="forecast length (hour)")
    PARSER.add_argument('--analysis_time_interval', type=str, 
                        required=True, help="analysis time increment")
    PARSER.add_argument('--obsproc_installation', type=str, 
                        required=True, help="obsproc installation")
    PARSER.add_argument('--wrf_interp_installation', type=str, 
                        required=True, help="wrf_interp installation")
    PARSER.add_argument('--met_installation', type=str, 
                        required=True, help="met installation")

    # -----------------
    # optional
    # -----------------
    PARSER.add_argument('--work_dir', type=str, 
                        required=False, default=os.getcwd(), help='working dir')
    PARSER.add_argument('--new_run', dest = 'new_run', default=False, 
                        help="delete the old data and create a new run",action='store_true')
    
    # -----------------
    # download data from s3/ddb (download_obs, download_fcst)
    # -----------------
    PARSER.add_argument('--download_obs', dest = 'download_obs', default=False, 
                        help="download observation in little_r",action='store_true')
    PARSER.add_argument('--download_fcst', dest = 'download_fcst', default=False, 
                        help="download wrfout from S3",action='store_true')
   
    # -----------------
    # run observation preprocessing (obsproc => obs2ascii => ascii2nc)
    # -----------------
    PARSER.add_argument('--run_obspreprocess', dest = 'run_obspreprocess', default=False, 
                        help="run all obs preprcessing tasks: \
                        run_obsproc + run_obs2ascii + run_ascii22nc", 
                        action='store_true')
    PARSER.add_argument('--run_obsproc', dest = 'run_obsproc', default=False, 
                        help="run obsproc to little_r",action='store_true')
    PARSER.add_argument('--run_obs2ascii', dest = 'run_obs2ascii', default=False, 
                        help="covert obsproc output to the \
                            format required by ascii2nc",action='store_true')
    PARSER.add_argument('--run_ascii2nc', dest = 'run_ascii2nc', default=False, 
                        help="run ascii2nc from MET",action='store_true')
    PARSER.add_argument('--ascii2nc_config', type=str, required=False,
                        help="ascii2nc config")


    # -----------------
    # run fcst preprocessing (wrf_interp)
    # -----------------
    PARSER.add_argument('--run_wrf_interp', dest = 'run_wrf_interp', default=False, 
                        help="run wrf_interp",action='store_true')
    PARSER.add_argument('--model', type=str, default=None, help="model name")
    PARSER.add_argument('--domain_id', type=str, default='2', help="domain ID")

    # -----------------------
    # pointstat
    # -----------------------
    PARSER.add_argument('--run_pointstat', dest = 'run_pointstat', default=False, 
                        help="run pointstat from MET",action='store_true')
    PARSER.add_argument('--pointstat_config', type=str, required=False,
                        help="pointstat config")

   
    return PARSER.parse_args()
    
    
def main():
    args = setup_parser()
    
    # 0: set up the required directoriesobsproc_dir
    dir_dict = setup_dir(args.new_run, args.work_dir)
    if args.run_obspreprocess:
        args.run_obsproc = args.run_obs2ascii \
             = args.run_ascii2nc = True
    
    
    # ----------------------------------------------
    # 1. Process observations
    # ----------------------------------------------
    # 1.1: download little_r
    if args.download_obs:
        print 'download_obs has not been implemented yet'
    
    # 1.2: run obsproc
    if args.run_obsproc:
        print 'run_obsproc has not been implemented yet' 
    
    # 1.3: convert output from obsproc to the ascii format that required by ascii2nc (met)
    if args.run_obs2ascii:
        obsproc_data, processed_list = obs_processing.get_obsproc_obs(args, dir_dict['obsproc_dir'])
        obs_processing.obsproc2ascii(dir_dict['obs_ascii_dir'], obsproc_data, processed_list)
    
    # 1.4: run ascii2nc
    if args.run_ascii2nc:
        if not args.ascii2nc_config:
            raise Exception('Config for ascii2nc is missing (required by run_ascii2nc), use --ascii2nc_config')
        obs_processing.ascii2nc(dir_dict['obs_ascii_dir'], dir_dict['obs_ascii2nc'],
                     args.met_installation, args.ascii2nc_config)
    
    # ----------------------------------------------
    # 2. Process forecast
    # ----------------------------------------------
    # 2.1: download forecast
    if args.download_fcst:
        print 'download_fcst has not been implemented yet'
    
    # 2.2: run wrf_interp
    if args.run_wrf_interp:
        if not (args.model and args.domain_id):
            raise Exception('--model and --domain_id are required by --run_wrf_interp')
        fcst_processing.wrf_interp(args, dir_dict['fcst_dir'], 
                                   dir_dict['wrf_interp_dir'])
        
    # ----------------------------------------------
    # 3. run point_stat
    # ----------------------------------------------        
    # 3.1 run point_stat
    if args.run_pointstat:
        if not args.pointstat_config:
            raise Exception('--pointstat_config is required by --run_pointstat')
        met_processing.run_pointstat(args, dir_dict,
                                     args.pointstat_config)
        


  
if __name__ == '__main__':
    main()
    