#!/usr/bin/env python

import subprocess
import os
from datetime import datetime, timedelta
import shutil

'''
This program is used to run start_met.py multiple times (with multi models)
Modify the following parameters to suite your needs:
 * download_obs:         whether (re)download and process the obseration
 * a_new_run:            if True: the verification work directory will be recreated, old one would be deleted
 * general_config:       Some shared parameters
 * multi_met_config:     Model specific parameters
'''

############################
#User should modify the following parameters
############################

download_obs = True
a_new_run = True

general_config = {
    'work_dir': '/mnt/WRF/met',
    'obs_download_dir': '/mnt/WRF/met/obs',
    'obsproc_installation': '/opt/miniconda2/envs/met/wrfda/WRFDA/var/obsproc',
    'wrf_interp_installation': '/opt/miniconda2/envs/met/wrf_interp',
    'met_installation': '/opt/miniconda2/envs/met/met',
    'ascii2nc_config': '/opt/miniconda2/envs/met/lib/python2.7/site-packages/run_met/../../../../run_met/etc/ascii2nc.config',
    'pointstat_config': '/opt/miniconda2/envs/met/lib/python2.7/site-packages/run_met/../../../../run_met/etc/pointstat.config'
    } 

multi_met_config = {
    'start_analysis': ['201712250000', 
                       '201712250000',
                       '201712250100', '201712250200'],
    'end_analysis': ['201712250000', 
                     '201712250000',
                     '201712250100','201712250200'],
    'forecast_length': [6, 6, 6, 6],
    'analysis_time_interval': [1, 1, 1, 1],
    'model': ['nz8kmN-NCEP', 'nz8kmN-NCEP-obsnudge-39', 'nz8kmN-NCEP-var', 'nz8kmN-NCEP-var'],
    'model_name': ['NCEP8', 'NCEP8n', 'NCEP8v', 'NCEP8v'],
    'domain_id': [2, 2, 2, 2],
    'download_fcst_source':[
        'internal',
        'internal',
        'internal', 'internal'],
    }


############################
# Unless it is necessary, user should not touch any of the codes below
############################

def setup_cmd():
    
    # 1.0: check the inputs 
    if a_new_run:
        if os.path.exists(general_config['work_dir']):
            shutil.rmtree(general_config['work_dir'])
        os.makedirs(general_config['work_dir'])
        
    model_no = len(multi_met_config['start_analysis'])
    print 'There are {} models to be verified'.format(model_no)
    for i in range(0, model_no):
        print '   * {}'.format(multi_met_config['model'][i])
    
    for cur_key in multi_met_config.keys():
        if len(multi_met_config[cur_key]) < model_no:
            raise Exception('the number of key {} is not consistent'.format(cur_key))
    
    if download_obs:
        # 2.0 download all the required observations and process them at one time
        print '<><><><><><><><><><><><><><><><><><><>'
        print 'download observations'
        print '<><><><><><><><><><><><><><><><><><><>'
        obs_download_dir = general_config['obs_download_dir']
        
        start_analysis_in_datetime = [datetime.strptime(i, '%Y%m%d%H%M') 
                                      for i in multi_met_config['start_analysis']]
        end_analysis_in_datetime = [datetime.strptime(i, '%Y%m%d%H%M') 
                                      for i in multi_met_config['end_analysis']]
        earliest_obs_datetime = min(start_analysis_in_datetime)
        latest_obs_datetime = max(end_analysis_in_datetime) + timedelta(seconds = max(
            multi_met_config['forecast_length'])*3600)
        cur_cmd = 'start_met.py --start_analysis {} --end_analysis {} \
            --forecast_length {} --analysis_time_interval {} --new_run \
            --obsproc_installation {} --wrf_interp_installation {} \
            --met_installation {} --work_dir {} --model obs \
            --download_obs --run_obspreprocess --ascii2nc_config {}'.format(earliest_obs_datetime.strftime('%Y%m%d%H%M'),
                                   earliest_obs_datetime.strftime('%Y%m%d%H%M'),
                                   int((latest_obs_datetime - earliest_obs_datetime).total_seconds()/3600.0),
                                   1,             
                                   general_config['obsproc_installation'],
                                   general_config['wrf_interp_installation'],
                                   general_config['met_installation'], obs_download_dir,
                                   general_config['ascii2nc_config'])
        p1 = subprocess.Popen(cur_cmd, cwd=os.getcwd(), shell=True)
        p1.wait()

    obs_nc_path = os.path.join(general_config['obs_download_dir'], 'ascii2nc', 'obs_ascii.nc')

    # 3.0 start verifications
    cur_pointstat_config = general_config['pointstat_config']
    for i in range(0, model_no):
        print '<><><><><><><><><><><><><><><><><><><>'
        print 'start verifying {}'.format(multi_met_config['model'][i])
        print '<><><><><><><><><><><><><><><><><><><>'
        
        cur_start_analysis = multi_met_config['start_analysis'][i]
        cur_end_analysis = multi_met_config['end_analysis'][i]
        cur_forecast_length = multi_met_config['forecast_length'][i]
        cur_analysis_time_interval = multi_met_config['analysis_time_interval'][i]
        cur_model = multi_met_config['model'][i]
        cur_model_name = multi_met_config['model_name'][i]
        cur_domain_id = multi_met_config['domain_id'][i]
        cur_download_fcst_source = multi_met_config['download_fcst_source'][i]

        cur_cmd = 'start_met.py --start_analysis {} --end_analysis {} \
        --forecast_length {} --analysis_time_interval {} \
        --obsproc_installation {} --wrf_interp_installation {} \
        --met_installation {} --work_dir {} \
        --model {} --domain_id {} \
        --pre_download_obs {} --download_fcst \
        --run_wrf_interp --run_pointstat \
        --download_fcst_source {} \
        --pointstat_config {}'.format(
            cur_start_analysis, cur_end_analysis,
            cur_forecast_length, cur_analysis_time_interval,
            general_config['obsproc_installation'],
            general_config['wrf_interp_installation'],
            general_config['met_installation'],
            os.path.join(general_config['work_dir'], cur_model_name),
            cur_model, cur_domain_id, obs_nc_path,
            cur_download_fcst_source,
             cur_pointstat_config
            )
        print cur_cmd
        p1 = subprocess.Popen(cur_cmd, cwd=os.getcwd(), shell=True)
        p1.wait()

    print '-------------------------------------------'
    print 'Final results: {}'.format(general_config['work_dir'])
    print '-------------------------------------------'
    
if __name__ == '__main__':
    setup_cmd()
