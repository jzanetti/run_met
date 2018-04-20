#!/usr/bin/env python

import subprocess
import os
from datetime import datetime, timedelta
import shutil
import threading
'''
This program is used to run start_met.py + start_ver.py multiple times (with multi models)
Modify the following parameters to suite your needs:
 * download_obs:         whether (re)download and process the obseration
 * a_new_run:            if True: the verification work directory will be recreated, old one would be deleted
 * general_config:       Some shared parameters
 * multi_met_config:     Model specific parameters
 
start_met.py is used to provide fcst and obs
start_ver.py is used for verification


Note for the rainfall verification:
  * Note that if you want to run rainfall-radar verification, you need to run 
    "start_multiple_radar.py" before this script to download the required radar data
    from "start_multiple_radar.py", you will have "output" directory, and this
    "output" would be "radar_download_dir" in this script
  * if radar_download_dir is provided but no data being available there, none of
    the verifications will be carried out, so if you don't want the rainfall 
    verification, simply set radar_download_dir=None
'''

############################
#User should modify the following parameters
############################

download_obs = False
download_fcst = False
run_ver = True
a_new_run = False
run_radar_verification = True
run_conv_verification = False
scale_the_model = False

general_config = {
    'work_dir': '/tmp/met',
    'obs_download_dir': '/tmp/met/obs',
    'fcst_download_dir': '/tmp/met/fcst',
    'obsproc_installation': '/home/szhang/Programs/WRFDA_V3.9.1/WRFDA/var/obsproc',
    'wrf_interp_installation': '/home/szhang/Programs/anaconda2/envs/radar2/wrf_interp',
    'met_installation': None,
    } 

multi_met_config = {
    'start_analysis': ['201802200000', '201802200100', '201802200100', '201802200100'],
    'end_analysis': ['201802200000', '201802200100', '201802200100', '201802200100'],
    'forecast_length': [12, 12, 12, 12],
    'analysis_time_interval': [1, 1, 1, 1],
    'model': ['nz8kmN-NCEP-obsnudge-39', 'gsi_rad_only', 'combined_rad_only', 'wrfda_rad_only'],
    'model_name': ['obsnudge', 'gsi', 'combined', 'wrfda'],
    'domain_id': [2, 2, 2, 2],
    'radar_verification_thres': [2.5, 2.5, 2.5, 2.5],
    'download_fcst_unique_id': ['12345','12345','12345','12345'],
    'download_fcst_source':[
        's3://metservice-research-us-west-2/research/experiments/sijin/OnDemand/cyclone_gita/output',
        's3://metservice-research-us-west-2/research/experiments/sijin/OnDemand/cyclone_gita/output',
        's3://metservice-research-us-west-2/research/experiments/sijin/OnDemand/cyclone_gita/output',
        's3://metservice-research-us-west-2/research/experiments/sijin/OnDemand/cyclone_gita/output'],
    'radar_download_dir': ['/home/szhang/data/radar/new',
                           '/home/szhang/data/radar/new',
                           '/home/szhang/data/radar/new',
                           '/home/szhang/data/radar/new']
    }


############################
# Unless it is necessary, user should not touch any of the codes below
############################

def run_cmd(cur_cmd, doomy_one):
    p1 = subprocess.Popen(cur_cmd, cwd=os.getcwd(), shell=True)
    p1.wait()

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
        cur_cmd = ('start_met.py --start_analysis {} --end_analysis {} ' + 
            '--forecast_length {} --analysis_time_interval {} --new_run ' + 
            '--obsproc_installation {} --wrf_interp_installation {} ' + 
            '--met_installation {} --work_dir {} --model obs ' + 
            '--download_obs --run_obsproc --run_obs2ascii').format(earliest_obs_datetime.strftime('%Y%m%d%H%M'),
                                   earliest_obs_datetime.strftime('%Y%m%d%H%M'),
                                   int((latest_obs_datetime - earliest_obs_datetime).total_seconds()/3600.0),
                                   1,             
                                   general_config['obsproc_installation'],
                                   general_config['wrf_interp_installation'],
                                   general_config['met_installation'], obs_download_dir)
        p1 = subprocess.Popen(cur_cmd, cwd=os.getcwd(), shell=True)
        p1.wait()

    obs_ascii = general_config['obs_download_dir']

    # 3.0 downlaoad fcst
    if download_fcst:
        cmd_thread = []
        for i in range(0, model_no):
            print '<><><><><><><><><><><><><><><><><><><>'
            print 'start download {}'.format(multi_met_config['model'][i])
            print '<><><><><><><><><><><><><><><><><><><>'
            
            cur_start_analysis = multi_met_config['start_analysis'][i]
            cur_end_analysis = multi_met_config['end_analysis'][i]
            cur_forecast_length = multi_met_config['forecast_length'][i]
            cur_analysis_time_interval = multi_met_config['analysis_time_interval'][i]
            cur_model = multi_met_config['model'][i]
            cur_model_name = multi_met_config['model_name'][i]
            cur_domain_id = multi_met_config['domain_id'][i]
            cur_download_fcst_source = multi_met_config['download_fcst_source'][i]
            cur_fcst_unique_id = multi_met_config['download_fcst_unique_id'][i]
            
            cur_cmd = 'start_met.py --start_analysis {} --end_analysis {} \
            --forecast_length {} --analysis_time_interval {} \
            --obsproc_installation {} --wrf_interp_installation {} \
            --met_installation {} --work_dir {} \
            --model {} --domain_id {} \
             --download_fcst \
            --download_fcst_unique_id {} \
            --run_wrf_interp  \
            --download_fcst_source {} \
            '.format(
                cur_start_analysis, cur_end_analysis,
                cur_forecast_length, cur_analysis_time_interval,
                general_config['obsproc_installation'],
                general_config['wrf_interp_installation'],
                general_config['met_installation'],
                os.path.join(general_config['fcst_download_dir'], cur_model_name),
                cur_model, cur_domain_id,
                cur_fcst_unique_id,
                cur_download_fcst_source)
            
            cmd_thread.append(threading.Thread(target=run_cmd, args = (cur_cmd, 'doomy')))
        
        for tq in cmd_thread:
            tq.start()
        
        for tq in cmd_thread:
            tq.join()
            
    # 4.0: start ver
    if run_ver:
        cmd_thread = []
        for i in range(0, model_no):
            print '<><><><><><><><><><><><><><><><><><><>'
            print 'start verification {}'.format(multi_met_config['model'][i])
            print '<><><><><><><><><><><><><><><><><><><>'
            cur_start_analysis = multi_met_config['start_analysis'][i]
            cur_end_analysis = multi_met_config['end_analysis'][i]
            cur_forecast_length = multi_met_config['forecast_length'][i]
            cur_analysis_time_interval = multi_met_config['analysis_time_interval'][i]
            cur_model = multi_met_config['model'][i]
            cur_model_name = multi_met_config['model_name'][i]
            cur_domain_id = multi_met_config['domain_id'][i]
            radar_download_dir = multi_met_config['radar_download_dir'][i]
            cur_radar_verification_thres = multi_met_config['radar_verification_thres'][i]

            cur_cmd = 'start_ver.py --start_analysis {} --end_analysis {} \
                --forecast_length {} --analysis_time_interval {} \
                --pre_download_obs {} --pre_download_fcst {} \
                --model_list {} --domain_id {} --work_dir {} --pre_download_radar {} \
                --radar_verif_thres {}'.format(
                    cur_start_analysis, cur_end_analysis,
                    cur_forecast_length, cur_analysis_time_interval,
                    general_config['obs_download_dir'],
                    os.path.join(general_config['fcst_download_dir'], cur_model_name),
                    multi_met_config['model'][i], 2,
                    general_config['work_dir'], radar_download_dir, cur_radar_verification_thres)

            if run_radar_verification:
                cur_cmd = cur_cmd + ' --run_radar_verification'
            if run_conv_verification:
                cur_cmd = cur_cmd + ' --run_conv_verification'
            if scale_the_model:
                cur_cmd = cur_cmd + ' --scale_the_model'

            cmd_thread.append(threading.Thread(target=run_cmd, args = (cur_cmd, 'doomy')))
        
        for tq in cmd_thread:
            tq.start()
        
        for tq in cmd_thread:
            tq.join()

    print '-------------------------------------------'
    print 'Final results: {}'.format(general_config['work_dir'])
    print '-------------------------------------------'
    
if __name__ == '__main__':
    setup_cmd()
