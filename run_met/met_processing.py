from datetime import datetime, timedelta
import os
import subprocess
from glob import glob

def run_pointstat(args, dir_dict, pointstat_config):
    if not os.path.exists(os.path.join(dir_dict['point_stat_dir'], 'point_stat')):
        os.symlink(os.path.join(args.met_installation, 'bin', 'point_stat'), 
                       os.path.join(dir_dict['point_stat_dir'], 'point_stat'))
    
    if not os.path.exists(os.path.join(dir_dict['point_stat_dir'], 'pointstat.config')):
        os.symlink(pointstat_config, 
                   os.path.join(dir_dict['point_stat_dir'], 'pointstat.config'))
    
    obs_path = os.path.join(dir_dict['obs_ascii2nc'], 'obs_ascii.nc')
    
    cur_analysis_time = args.start_analysis_time
    
    while cur_analysis_time <= args.end_analysis_time:
        cur_analysis_dir = os.path.join(dir_dict['fcst_dir'],
                                        cur_analysis_time.strftime('%Y%m%d%H'))
        cur_fcst_filename_list = glob(cur_analysis_dir + '/*')
        
        out_dir = os.path.join(dir_dict['point_stat_dir'],
                                cur_analysis_time.strftime('%Y%m%d%H'))
        
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        
        for cur_fcst_filename in cur_fcst_filename_list:
            cur_fcst_path = os.path.join(cur_analysis_dir, cur_fcst_filename)
            
            point_stat_cmd = './point_stat {} {} {} -outdir {}'.format(cur_fcst_path, 
                                                            obs_path,
                                                            'pointstat.config',
                                                            out_dir)
            
            p1 = subprocess.Popen(point_stat_cmd, cwd=dir_dict['point_stat_dir'], shell=True)
            p1.wait()
        
        cur_analysis_time = cur_analysis_time + \
                timedelta(seconds = 3600*int(args.analysis_time_interval))
            
    