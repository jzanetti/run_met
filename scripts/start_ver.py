#!/usr/bin/env python

######################################
# start_ver is a program providing the basic verification results 
# from WRF, it covers RMSE for temperature, relative huimidity, U/V
# and CSI/FAR for precipitation

# start_ver requres to run start_met to get the required obs

# it can be used as an alternative to the point_stat application 
# from MET

# Author: Sijin

# in order to run this script, you must run start_met.py to download
# and process observations and forecasts

######################################

'''
debug:
    return PARSER.parse_args(['--start_analysis_time', '201712250000',
                              '--end_analysis_time', '201712250000',
                              '--analysis_time_interval', '1',
                              '--forecast_length', '1',
                              '--pre_download_obs', '/tmp/met/obs',
                              '--pre_download_fcst', '/tmp/met/NCEP8',
                              '--model_list', 'nz8kmN-NCEP',
                              '--domain_id', '2',
                              '--work_dir', '/tmp/ver/'])
'''

import argparse
from datetime import datetime

from run_met import ver_processing


def valid_datetime(timestamp):
    '''turn a timestamp into a datetime object'''
    try:
        return datetime.strptime(timestamp, "%Y%m%d%H%M")
    except ValueError:
        msg = "Not a valid date: '{}'.".format(timestamp)
    raise argparse.ArgumentTypeError(msg)

def setup_parser():
    """run verifications"""
    PARSER = argparse.ArgumentParser(
            description='run verifications')
    
    PARSER.add_argument('--start_analysis_time', type=valid_datetime, 
                        required=True, help="start analysis time (YYYYMMDDHHM)")
    PARSER.add_argument('--end_analysis_time', type=valid_datetime, 
                        required=True, help="end analysis time (YYYYMMDDHHM)")
    PARSER.add_argument('--analysis_time_interval', type=str, 
                        required=True, help="analysis_time_interval (hour)")
    PARSER.add_argument('--forecast_length', type=str, 
                        required=True, help="forecast length (hour)")
    PARSER.add_argument('--pre_download_obs', type=str,  
                        required=True, help="pre_download_obs")
    PARSER.add_argument('--pre_download_fcst', type=str, 
                        required=True, help="pre_download_fcst")
    PARSER.add_argument('--model_list', nargs='+', 
                        required=True, help="model name")
    PARSER.add_argument('--domain_id', type=str, 
                        required=True, help="model name")
    PARSER.add_argument('--work_dir', type=str,  
                        required=True, help="model name")
    
    return PARSER.parse_args()
        

if __name__ == '__main__':
    args = setup_parser()
    
    ver_processing.setup_ver(args)

    print 'done'
                
    

    
