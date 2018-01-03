from datetime import datetime, timedelta
import os
import subprocess
from glob import glob

from AMPSAws import resources

rinstance=resources.running_on_ec2()

def download_fcst(args, fcst_dir):
    """download fcst files into $fcst_dir/$cur_analysis_time/wrf_hourly*
    """
    if not rinstance:
        raise Exception('download_fcst must be run in the EC2 box')

    cur_analysis_time = args.start_analysis_time

    while cur_analysis_time <= args.end_analysis_time:
        cur_local_fcst_dir = \
            os.path.join(fcst_dir, cur_analysis_time.strftime('%Y%m%d%H'))
        cur_remote_fcst_dir = os.path.join(
            args.download_fcst_source, args.model,
            cur_analysis_time.strftime('%y/%m/%d/%H'))
        for fcst_h in range(1, int(args.forecast_length)+1):
            cur_valid_t = cur_analysis_time + timedelta(seconds = fcst_h*3600)
            cur_remote_fcst_filename = \
                'wrf_hourly_{}_d0{}_{}'.format(
                    args.model, args.domain_id,
                    cur_valid_t.strftime('%Y-%m-%d_%H:00:00')
                    )
            cur_remote_fcst_path = os.path.join(cur_remote_fcst_dir,
                                                cur_remote_fcst_filename)
            cur_local_fcst_path = os.path.join(cur_local_fcst_dir,
                                               cur_remote_fcst_filename)
            resources.copy(cur_remote_fcst_path, cur_local_fcst_path)

        cur_analysis_time = cur_analysis_time + \
                timedelta(seconds = 3600*int(args.analysis_time_interval))


def wrf_interp_namelist(path_to_input, path_to_output,
                        root_name, grid_id,
                        start_date,
                        interp_levels,
                        wrf_interp_dir):
    """create the wrf_interp namelist
        (1) interp_levels examples:
            1000,800,5500,100,12.5
            (You need at least two interpolation levels.
            The program will not interpolate just one level.
            Expected values for vert_coordinate along with units)

        (2) vert_coordinate:
            pressure, pres            hPa
            log_pres                  hPa
            ght_msl                   km
            ght_agl                   km
            theta                     K
            thea-e                    K

    """
    namelist_field = {
        '&io': {'path_to_input': path_to_input,
                'path_to_output': path_to_output,
                'root_name': root_name,
                'grid_id': grid_id,
                'start_date': start_date,
                'leap_year': True,
                'debug': True},
        '&interp_in':{'interp_levels': interp_levels,
                   'extrapolate': 1,
                   'unstagger_grid':False, 'vert_coordinate': 'pres'}
            }
    
    target = open('{}/namelist.vinterp'.format(wrf_interp_dir), 'w')

    for r1 in ['&io', '&interp_in']:
        target.write(r1 + '\n')
        for r2 in namelist_field[r1].keys():
            target.write('  ')
            if isinstance((namelist_field[r1][r2]), bool):
                target.write(r2 + '=.' + str(namelist_field[r1][r2]).upper() + '.\n')
            elif isinstance((namelist_field[r1][r2]), list):
                target.write(r2 + '=' + ','.join([str(i) for i in namelist_field[r1][r2]]) + '.\n')
            elif isinstance((namelist_field[r1][r2]), str):
                target.write(r2 + '=\'' + str(namelist_field[r1][r2]) + '\'\n')
            else:
                target.write(r2 + '=' + str(namelist_field[r1][r2]) + '\n')
        target.write('/\n')
    
    target.close()

def wrf_interp(args, fcst_dir, wrf_interp_dir):

    if not os.path.exists(os.path.join(wrf_interp_dir, 'wrf_interp.exe')):
        os.symlink(os.path.join(args.wrf_interp_installation, 'wrf_interp.exe'), 
                    os.path.join(wrf_interp_dir, 'wrf_interp.exe'))
    
    cur_analysis_time = args.start_analysis_time
    
    while cur_analysis_time <= args.end_analysis_time:
        
        path_to_input = os.path.join(fcst_dir, cur_analysis_time.strftime('%Y%m%d%H'))
        path_to_output = os.path.join(wrf_interp_dir, cur_analysis_time.strftime('%Y%m%d%H'))
        root_name = 'wrf_hourly_' + args.model
        grid_id = int(args.domain_id)
        
        
        if not os.path.exists(path_to_output):
            os.makedirs(path_to_output)

        for fcst_h in range(1, int(args.forecast_length) + 1):
            start_date = (cur_analysis_time + timedelta(seconds = fcst_h*3600.0)).strftime('%Y-%m-%d_%H')
            interp_levels = [1000, 800, 700, 500, 250]
            
            wrf_interp_namelist(path_to_input, path_to_output,
                                    root_name, grid_id,
                                    start_date,
                                    interp_levels,
                                    wrf_interp_dir)

            p1 = subprocess.Popen('./wrf_interp.exe', cwd=wrf_interp_dir, shell=True)    
            p1.wait()
        
        cur_analysis_time = cur_analysis_time + \
                timedelta(seconds = 3600*int(args.analysis_time_interval))
            
            
            
            
