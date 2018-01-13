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

def start_check(args):
    if args.run_cnt and (not args.cnt_field_list):
        raise Exception('Required CNT fields')

    if args.run_mpr and (not args.mpr_field_list):
        raise Exception('Required MPR fields')
    
    if args.run_da_analysis and len(args.model_list) != 2:
        raise Exception('da analysis is switched on, 2 models are required')

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

    #######################
    # 1. required
    #######################
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
                        required=True, 
                        help="model name")
    PARSER.add_argument('--run_mpr', dest = 'run_mpr', default=True, 
                        help="run mpr plots (under tests)",action='store_true')
    PARSER.add_argument('--run_cnt', dest = 'run_cnt', default=True, 
                        help="run mpr plots (under tests)",action='store_true')
    
    
    #######################
    # 1.1 get the verification from start_met or start_ver
    #######################
    PARSER.add_argument('--data_from_ver', dest = 'data_from_ver', default=False, 
                        help="if point_stat is produced by ver \
                              [default: point_stat is from MET]",action='store_true')
    
    
    #######################
    # 1.2 optional (for cnt)
    #######################
    PARSER.add_argument('--cnt_field_list', nargs='+', required=False,
                        help="fcst fields to be plotted, e.g., T2")
    
    #######################
    # 1.3 optional (for mpr)
    #######################
    PARSER.add_argument('--mpr_field_list', nargs='+', required=False,
                        help="mpr fields to be plotted, e.g., T2")


    return PARSER.parse_args()

if __name__ == '__main__':
    args = setup_parser()
    
    print 'there are {} models to be plotted'.format(len(args.model_list))

    cur_met_task = args.met_task
    stats_output = {}
    
    if args.run_mpr:
        for mpr_field in args.mpr_field_list:
            plot_processing.return_mpr(args, mpr_field)

    if args.run_cnt:
        stats_output = plot_processing.return_cnt_cts(args, stats_output)
        plot_processing.plot_score(args, stats_output)
        
    print 'done'
            
                               
                                   
