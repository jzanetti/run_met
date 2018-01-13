#!/usr/bin/env python

import argparse
from run_met import plot_processing

"""
debug:
    return PARSER.parse_args(['--model1_mpr_path', '/home/jzanetti/Desktop/run_ver/met2/NCEP8/met_dir/point_stat/17122500/point_stat_010000L_20171225_010000V_mpr.txt',
                              '--model2_mpr_path', '/home/jzanetti/Desktop/run_ver/met2/NCEP8v/met_dir/point_stat/17122501/point_stat_010000L_20171225_020000V_mpr.txt',
                              '--model1_name', 'nz8kmN-NCEP',
                              '--model2_name', 'nz8kmN-NCEP-var',
                              '--fields_list', 'T2', 'UU'])
"""


def setup_parser():
    """plot verifications from MET"""
    PARSER = argparse.ArgumentParser(
            description='plot verifications from MET')
    
    PARSER.add_argument('--model1_mpr_path', type=str, 
                        required=True, help='model1_mpr_path')
    PARSER.add_argument('--model2_mpr_path', type=str, 
                        required=True, help='model2_mpr_path')
    PARSER.add_argument('--model1_name', type=str, 
                        required=True, help='model1 name')
    PARSER.add_argument('--model2_name', type=str, 
                        required=True, help='model2 name')
    PARSER.add_argument('--fields_list', nargs='+', 
                        required=True, 
                        help="field list such as T2")
    
    return PARSER.parse_args()

if __name__ == '__main__':
    args = setup_parser()

    for da_field in args.fields_list:
        plot_processing.return_two_model_comparisons(args, da_field)
