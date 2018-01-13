#!/usr/bin/env python

from datetime import datetime, timedelta
import os
from shutil import copyfile
import subprocess

'''
This program is used to produce the stats to compare 
the background and analysis with the observations

Step1: get the observation at the analysis time
Step2: copy the background analysis from ***/grb directory in /var/gsi
Step3: Run verification at both the bkg and analysis and produce
       the verification in the format of MET
'''

general_config = {
    'work_dir': '/mnt/WRF/da_tunning',
    'obsproc_installation': '/opt/miniconda2/envs/met/wrfda/WRFDA/var/obsproc',
    'wrf_interp_installation': '/opt/miniconda2/envs/met/wrf_interp',
    'met_installation': '/opt/miniconda2/envs/met/met',
    }

obs_config = {
    'obs_time': '201712250100'
    }

background_config = {
    'background': '/mnt/WRF/wrf_otDzvL/var/grb/wrfinput_d02_background',
    'analysis': '/mnt/WRF/wrf_otDzvL/var/grb/wrfinput_d02'
    
    }


def setup_obs_cmd():
    obs_dummy_ana_time = datetime.strptime(obs_config['obs_time'], '%Y%m%d%H%M') \
                        - timedelta(seconds=3600)
    obs_dummy_ana_time_str = obs_dummy_ana_time.strftime('%Y%m%d%H%M')
    get_obs_cmd = 'start_met.py --new_run --start_analysis_time {} --end_analysis_time {} --forecast_length 1 \
                   --analysis_time_interval 1 --obsproc_installation {} --wrf_interp_installation {} --met_installation {} \
                   --work_dir {} --model obs --domain_id 2 \
                   --download_obs --run_obsproc --run_obs2ascii'.format(obs_dummy_ana_time_str, obs_dummy_ana_time_str,
                                                            general_config['obsproc_installation'],
                                                            general_config['wrf_interp_installation'],
                                                            general_config['met_installation'],
                                                            general_config['work_dir'])
    
    return get_obs_cmd

def copy_data():
    fcst_dummy_ana_time = datetime.strptime(obs_config['obs_time'], '%Y%m%d%H%M') \
                        - timedelta(seconds=3600)
    fcst_dummy_ana_time_str1 = fcst_dummy_ana_time.strftime('%y%m%d%H')
    background_dir = os.path.join(general_config['work_dir'], 'background', 'fcst', fcst_dummy_ana_time_str1)
    analysis_dir = os.path.join(general_config['work_dir'], 'analysis', 'fcst', fcst_dummy_ana_time_str1)
    
    if not os.path.exists(background_dir):
        os.makedirs(background_dir)

    if not os.path.exists(analysis_dir):
        os.makedirs(analysis_dir) 
    
    # wrf_hourly_nz8kmN-NCEP-var_d01_2017-12-25_01:00:00
    background_filename = 'wrf_hourly_background_d02_{}:00:00'.format(
        datetime.strptime(obs_config['obs_time'], '%Y%m%d%H%M').strftime('%Y-%m-%d_%H'))

    analysis_filename = 'wrf_hourly_analysis_d02_{}:00:00'.format(
        datetime.strptime(obs_config['obs_time'], '%Y%m%d%H%M').strftime('%Y-%m-%d_%H'))
    
    copyfile(background_config['background'], os.path.join(background_dir, background_filename))
    copyfile(background_config['analysis'], os.path.join(analysis_dir, analysis_filename))
    
def setup_ver_cmd():
    fcst_dummy_ana_time = datetime.strptime(obs_config['obs_time'], '%Y%m%d%H%M') \
                        - timedelta(seconds=3600)
    fcst_dummy_ana_time_str = fcst_dummy_ana_time.strftime('%Y%m%d%H')
    
    cur_background_prepcess_cmd = 'start_met.py --start_analysis {} --end_analysis {} \
            --forecast_length 1 --analysis_time_interval 1 \
            --obsproc_installation {} --wrf_interp_installation {} \
            --met_installation {} --work_dir {} \
            --model background --domain_id 2 \
            --run_wrf_interp'.format(
                fcst_dummy_ana_time_str, fcst_dummy_ana_time_str,
                general_config['obsproc_installation'],
                general_config['wrf_interp_installation'],
                general_config['met_installation'],
                os.path.join(general_config['work_dir'], 'background'))

    cur_analysis_prepcess_cmd = 'start_met.py --start_analysis {} --end_analysis {} \
            --forecast_length 1 --analysis_time_interval 1 \
            --obsproc_installation {} --wrf_interp_installation {} \
            --met_installation {} --work_dir {} \
            --model analysis --domain_id 2 \
            --run_wrf_interp'.format(
                fcst_dummy_ana_time_str, fcst_dummy_ana_time_str,
                general_config['obsproc_installation'],
                general_config['wrf_interp_installation'],
                general_config['met_installation'],
                os.path.join(general_config['work_dir'], 'analysis'))
        
    cur_background_cmd = 'start_ver.py --start_analysis {} --end_analysis {} \
                --forecast_length 1 --analysis_time_interval 1 \
                --pre_download_obs {} --pre_download_fcst {} \
                --model_list background --domain_id 2 --work_dir {}'.format(
                    fcst_dummy_ana_time_str, fcst_dummy_ana_time_str,
                    general_config['work_dir'], os.path.join(general_config['work_dir'], 'background'),
                    general_config['work_dir'])

    cur_analysis_cmd = 'start_ver.py --start_analysis {} --end_analysis {} \
                --forecast_length 1 --analysis_time_interval 1 \
                --pre_download_obs {} --pre_download_fcst {} \
                --model_list analysis --domain_id 2 --work_dir {}'.format(
                    fcst_dummy_ana_time_str, fcst_dummy_ana_time_str,
                    general_config['work_dir'], os.path.join(general_config['work_dir'], 'analysis'),
                    general_config['work_dir'])
    
    return cur_background_prepcess_cmd, cur_analysis_prepcess_cmd, cur_background_cmd, cur_analysis_cmd

if __name__ == '__main__':
    get_obs_cmd = setup_obs_cmd()
    cur_background_prepcess_cmd, cur_analysis_prepcess_cmd, \
            cur_background_cmd, cur_analysis_cmd = setup_ver_cmd()
    
    p1 = subprocess.Popen(get_obs_cmd, cwd=os.getcwd(), shell=True)
    p1.wait()

    copy_data()
    p1 = subprocess.Popen(cur_background_prepcess_cmd, cwd=os.getcwd(), shell=True)
    p1.wait()
    
    p1 = subprocess.Popen(cur_analysis_prepcess_cmd, cwd=os.getcwd(), shell=True)
    p1.wait()
    
    p1 = subprocess.Popen(cur_background_cmd, cwd=os.getcwd(), shell=True)
    p1.wait()
    
    p1 = subprocess.Popen(cur_analysis_cmd, cwd=os.getcwd(), shell=True)
    p1.wait()
    
    print 'done'
