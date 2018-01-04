#!/usr/bin/env python

import subprocess
import os

'''
This program is used to run start_met.py multiple times (with multi models)
'''

general_config = {
    'work_dir': '/mnt/WRF/met',
    'obsproc_installation': '/opt/miniconda2/envs/met/wrfda/WRFDA/var/obsproc',
    'wrf_interp_installation': '/opt/miniconda2/envs/met/wrf_interp',
    'met_installation': '/opt/miniconda2/envs/met/met',
    
    } 

multi_met_config = {
    'start_analysis': ['201712250000', 
                       '201712250000'],
    'end_analysis': ['201712250000', 
                     '201712250000'],
    'forecast_length': [6, 6],
    'analysis_time_interval': [1, 1],
    'model': ['nz8kmN-NCEP', 'nz8kmN-NCEP-obsnudge'],
    'domain_id': [2, 2],
    'download_fcst_source':[
        'internal',
        'internal'],
    'ascii2nc_config': [
        '/opt/miniconda2/envs/met/lib/python2.7/site-packages/run_met/../../../../run_met/etc/ascii2nc.config',
        '/opt/miniconda2/envs/met/lib/python2.7/site-packages/run_met/../../../../run_met/etc/ascii2nc.config'],
    'pointstat_config':[
        '/opt/miniconda2/envs/met/lib/python2.7/site-packages/run_met/../../../../run_met/etc/pointstat.config',
        '/opt/miniconda2/envs/met/lib/python2.7/site-packages/run_met/../../../../run_met/etc/pointstat.config'
        ],
    }

def setup_cmd():
    model_no = len(multi_met_config['start_analysis'])
    print 'There are {} models to be verified'.format(model_no)
    for i in range(0, model_no):
        print '   * {}'.format(multi_met_config['model'][i])
    
    for i in range(0, model_no):
        print '<><><><><><><><><><><><><><><><><><><>'
        print 'start verifying {}'.format(multi_met_config['model'][i])
        print '<><><><><><><><><><><><><><><><><><><>'
        
        cur_start_analysis = multi_met_config['start_analysis'][i]
        cur_end_analysis = multi_met_config['end_analysis'][i]
        cur_forecast_length = multi_met_config['forecast_length'][i]
        cur_analysis_time_interval = multi_met_config['analysis_time_interval'][i]
        cur_model = multi_met_config['model'][i]
        cur_domain_id = multi_met_config['domain_id'][i]
        cur_download_fcst_source = multi_met_config['download_fcst_source'][i]
        cur_ascii2nc_config = multi_met_config['ascii2nc_config'][i]
        cur_pointstat_config = multi_met_config['pointstat_config'][i]
        
        cur_cmd = 'start_met.py --start_analysis {} --end_analysis {} \
        --forecast_length {} --analysis_time_interval {} --new_run \
        --obsproc_installation {} --wrf_interp_installation {} \
        --met_installation {} --work_dir {} \
        --model {} --domain_id {} \
        --download_obs --download_fcst \
        --run_obspreprocess --run_wrf_interp --run_pointstat \
        --download_fcst_source {} \
        --ascii2nc_config {} --pointstat_config {}'.format(
            cur_start_analysis, cur_end_analysis,
            cur_forecast_length, cur_analysis_time_interval,
            general_config['obsproc_installation'],
            general_config['wrf_interp_installation'],
            general_config['met_installation'],
            os.path.join(general_config['work_dir'], cur_model),
            cur_model, cur_domain_id,
            cur_download_fcst_source,
            cur_ascii2nc_config, cur_pointstat_config
            )
        print cur_cmd
        p1 = subprocess.Popen(cur_cmd, cwd=os.getcwd(), shell=True)
        p1.wait()

    print '-------------------------------------------'
    print 'Final results: {}'.format(general_config['work_dir'])
    print '-------------------------------------------'
    
if __name__ == '__main__':
    setup_cmd()
