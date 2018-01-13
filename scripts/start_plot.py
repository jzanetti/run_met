#!/usr/bin/env python
import os
import argparse
from datetime import datetime, timedelta
import numpy
import matplotlib.pyplot as plt
from run_met import plot_processing

'''
plot the met outputs 

[debug command]:
    return PARSER.parse_args(['--start_analysis_time', '201712250000',
                              '--end_analysis_time', '201712250000',
                              '--forecast_length', '6',
                              '--analysis_time_interval', '1',
                              '--model_list', 'nz8kmN-NCEP', 'nz8kmN-NCEP-obsnudge',
                              '--met_task', 'point_stat',
                              '--met_out_dir', '/home/szhang/Desktop/run_ver/met',
                              '--plot_field_list', 'T2'])

[script command]:
    start_plot.py --start_analysis_time 201712250000 --end_analysis_time 201712250000 --forecast_length 6 
                  --analysis_time_interval 1 --model_list nz8kmN-NCEP nz8kmN-NCEP-obsnudge
                  --met_task point_stat
                  --met_out_dir /home/szhang/Desktop/run_ver/met
                  --plot_field_list T2
'''

def valid_datetime(timestamp):
    '''turn a timestamp into a datetime object'''
    try:
        return datetime.strptime(timestamp, "%Y%m%d%H%M")
    except ValueError:
        msg = "Not a valid date: '{}'.".format(timestamp)
    raise argparse.ArgumentTypeError(msg)

def setup_parser():
    """plot verifications from MET"""
    PARSER = argparse.ArgumentParser(
            description='plot verifications from MET')
    
    PARSER.add_argument('--start_analysis_time', type=valid_datetime, 
                        required=True, help="start analysis time (YYYYMMDDHHM)")
    PARSER.add_argument('--end_analysis_time', type=valid_datetime, 
                        required=True, help="end analysis time (YYYYMMDDHHM)")
    PARSER.add_argument('--forecast_length', type=str, 
                        required=True, help="forecast length (hour)")
    PARSER.add_argument('--analysis_time_interval', type=str, 
                        required=True, help="analysis time increment")
    PARSER.add_argument('--met_out_dir', type=str, 
                        required=True, help='working dir')
    PARSER.add_argument('--met_task', type=str, 
                        required=True, help='met_task, e.g., point_stat')
    PARSER.add_argument('--model_list', nargs='+', 
                        required=True, help="model name")
    PARSER.add_argument('--plot_field_list', nargs='+', required=True,
                        help="fcst fields to be plotted, e.g., T2")
    PARSER.add_argument('--run_mpr', dest = 'run_mpr', default=False, 
                        help="run mpr plots (under tests)",action='store_true')
    PARSER.add_argument('--data_from_ver', dest = 'data_from_ver', default=False, 
                        help="if point_stat is produced by ver",action='store_true')

    return PARSER.parse_args()

if __name__ == '__main__':
    args = setup_parser()
    
    print 'there are {} models to be plotted'.format(len(args.model_list))
    
    # 0: prepare the plots:
    cur_met_task = args.met_task
    stats_output = {}
    
    if args.run_mpr:
        plot_processing.return_mpr(args, 'RH')
    
    '''
    stats_output = plot_processing.return_cnt_cts(args, stats_output)
    plot_processing.plot_score(args, stats_output)
    '''
    print 'done'
            
                               
                                   
