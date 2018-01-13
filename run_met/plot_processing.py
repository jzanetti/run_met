from datetime import datetime, timedelta
import numpy
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
plt.switch_backend('agg')
import os


# configure the plot
task_list = {
    'score1': {'score_name': 'ME',
                'score_type': 'cnt',
                'met_task': 'point_stat',
                'bootstrap': 'BC',
                'condition_name': None,
                'condition_value': None
                },
    'score2': { 'score_name': 'MAE',
                'score_type': 'cnt',
                'met_task': 'point_stat',
                'bootstrap': None,
                'condition_name': ['FCST_THRESH', 'OBS_THRESH'],
                'condition_value': ['>273.0', '>273.0']
                },
    'score3': { 'score_name': 'RMSE',
                'score_type': 'cnt',
                'met_task': 'point_stat',
                'bootstrap': None,
                'condition_name': None,
                'condition_value': None
                },
             }

def get_stats_filename(args, cur_valid_time, cur_model, cur_met_task, cur_score_type, cur_lead_h):
    if not args.data_from_ver:
        if cur_model.endswith('n') or cur_model.endswith('nudge'):
            cur_lead_h = cur_lead_h + 6
        
    stats_filename = '{}_{:02d}0000L_{}0000V_{}.txt'.format(
            cur_met_task,
            cur_lead_h, cur_valid_time.strftime('%Y%m%d_%H'),
            cur_score_type)
    
    return stats_filename

def write_stats_output(stats_output, field_name, field_value):
    if not (field_name in stats_output.keys()):
        stats_output[field_name] = [field_value]
    else:
        stats_output[field_name].append(field_value)
    return stats_output

def read_mpr_stats(args, cur_stats_path, cur_field):
    """read mpr stats for all requested stations"""
    f_stats = open(cur_stats_path, "r")
    data_lines = f_stats.readlines()
    
    mpr_lat = []
    mpr_lon = []
    mpr_fcst = []
    mpr_obs = []
    mpr_time = []
    for i, cur_lines in enumerate(data_lines):
        if i == 0:
            mpr_header = filter(None, cur_lines.split(' '))
            mpr_var_index = mpr_header.index('FCST_VAR')
            mpr_lat_index = mpr_header.index('OBS_LAT')
            mpr_lon_index = mpr_header.index('OBS_LON')
            mpr_fcst_index = mpr_header.index('FCST')
            mpr_obs_index = mpr_header.index('OBS')
            mpr_time_index = mpr_header.index('FCST_VALID_END')
        else:
            cur_lines = filter(None, cur_lines.split(' '))
            if len(cur_lines) < 10:
                continue
            if cur_lines[mpr_var_index] == cur_field:
                mpr_lat.append(float(cur_lines[mpr_lat_index]))
                mpr_lon.append(float(cur_lines[mpr_lon_index]))
                mpr_fcst.append(float(cur_lines[mpr_fcst_index]))
                mpr_obs.append(float(cur_lines[mpr_obs_index]))
                mpr_time.append(cur_lines[mpr_time_index])
    
    return mpr_lat, mpr_lon, mpr_fcst, mpr_obs, mpr_time

def read_cnt_cts_stats(args, cur_score, cur_stats_path, cur_score_name, cur_field):
    """read stats value from the met output
    example: 
        cur_score: score1
        cur_stats_path: point_stat_060000L_20171225_060000V_cnt.txt
        cur_score_name: MAE
        cur_field: T2
        """
    score_value_list = None
    f_stats = open(cur_stats_path, "r")
    data_lines = f_stats.readlines()
    
    if len(data_lines) == 1:
        return numpy.NaN, numpy.NaN, numpy.NaN
    else:
        for i, cur_lines in enumerate(data_lines):
            cur_lines = cur_lines.strip()
            if i == 0:
                score_header = filter(None, cur_lines.split(' '))
            else:
                score_value_tmp = filter(None, cur_lines.split(' '))
                # step1: if this line contains the infomation for cur_field
                if score_value_tmp[score_header.index('FCST_VAR')] == cur_field:
                    
                    # step2: check if we need to add any conditions
                    condition_name = task_list[cur_score]['condition_name']
                    if condition_name:
                        all_condition_met = True
                        
                        # step 2.1: loop over all conditions
                        for c_con_name in condition_name:
                            req_cond_index = score_header.index(c_con_name)
                            if score_value_tmp[req_cond_index] == task_list[cur_score]['condition_value']:
                                all_condition_met = False
                                break
                            
                        if all_condition_met:
                            score_value_list = score_value_tmp
                    else:
                        score_value_list = score_value_tmp
    
    if not score_value_list:
        raise Exception('Cannot find the fcst field {}'.format(cur_field))

    if len(score_value_list) != len(score_header):
        raise Exception('score type length and score value length are not identical')
    
    # extract the values
    req_score_index = score_header.index(cur_score_name)
    if  score_value_list[req_score_index] != 'NA':
        found_score_value = float(score_value_list[req_score_index])
    else:
        found_score_value = None
    
    bootstrap_type = task_list[cur_score]['bootstrap']
    if bootstrap_type:
        upper_bs = score_header.index(cur_score_name + '_' + bootstrap_type + 'U')
        lower_bs = score_header.index(cur_score_name + '_' + bootstrap_type + 'L')
        found_score_upper_bs = score_value_list[upper_bs]
        found_score_lower_bs = score_value_list[lower_bs]
        if found_score_upper_bs == 'NA':
            found_score_upper_bs = None
            found_score_lower_bs = None
    else:
        found_score_upper_bs = None
        found_score_lower_bs = None
    
    return found_score_value, found_score_upper_bs, found_score_lower_bs


def return_mpr(args, cur_field):
    for i in range(0, len(args.model_list)):
        cur_model = args.model_list[i]
        cur_met_dir = os.path.join(args.met_out_dir, 
                                   cur_model, 'met_dir',
                                   args.met_task)
        
        # 2: loop over all analysis
        cur_analysis_time = args.start_analysis_time
        while cur_analysis_time <= args.end_analysis_time:
            cur_stats_dir = os.path.join(cur_met_dir, 
                                         cur_analysis_time.strftime('%y%m%d%H'))
            
            # 3: loop over all forecasts (at different valid times)
            for cur_lead_h in range(1, int(args.forecast_length)+1):
                cur_valid_time = cur_analysis_time + timedelta(seconds=cur_lead_h*3600)
                
                # 4.2 get the met output filepath
                cur_stats_filename = get_stats_filename(args, cur_valid_time, 
                                                            cur_model,
                                                            args.met_task,
                                                            'mpr',
                                                            cur_lead_h)
                cur_stats_path = os.path.join(cur_stats_dir, cur_stats_filename)
                mpr_lat, mpr_lon, mpr_fcst, mpr_obs, mpr_time = read_mpr_stats(args, cur_stats_path, cur_field)
                plot_mpr(mpr_lat, mpr_lon, mpr_fcst, mpr_obs, mpr_time,
                         cur_analysis_time, cur_valid_time, cur_model, cur_field)
            
            cur_analysis_time = cur_analysis_time + \
                timedelta(seconds = 3600*int(args.analysis_time_interval))


    
def plot_mpr(mpr_lat, mpr_lon, mpr_fcst, mpr_obs, mpr_time,
             cur_analysis_time, cur_valid_time, cur_model, cur_field):
    fig = plt.figure()
    m = Basemap(llcrnrlat=-48.75, urcrnrlat=-30.0,
                    llcrnrlon=164.5, urcrnrlon=181.50,
                    resolution='l', projection='cyl',
                    lat_1=-30, lat_2=-60.0,
                    lat_0=-40.7, lon_0=167.5)
    m.drawcoastlines()
    m.drawcountries()
    x, y = m(mpr_lon, mpr_lat)
    
    mpr_diff = list(numpy.asarray(mpr_fcst) - numpy.asarray(mpr_obs))

    cs = m.scatter(x, y, c=mpr_diff, s=300, marker="o", cmap=plt.get_cmap('bwr'))

    max_mpr_diff = max(abs(numpy.asarray(mpr_diff)))

    plt.clim([-max_mpr_diff, max_mpr_diff])

    cbar = m.colorbar(cs, location='bottom', pad="5%")
    cbar.set_label('fcst - obs')

    plt.title(cur_analysis_time.strftime('%Y%m%d%H') + ', V' + cur_valid_time.strftime('%Y%m%d%H') + \
               '\n' + cur_model + ', ' + cur_field)

    out_filename = cur_analysis_time.strftime('%Y%m%d%H') + '_' + cur_valid_time.strftime('%Y%m%d%H') + \
            '_' + cur_model + '_' + cur_field + '.png'
    plt.savefig(out_filename, bbox_inches='tight')
    plt.close()
                

def return_cnt_cts(args, stats_output):
    """store the extracted score values in a dict"""
    for i in range(0, len(args.model_list)):
        cur_model = args.model_list[i]
        cur_met_dir = os.path.join(args.met_out_dir, 
                                   cur_model, 'met_dir',
                                   args.met_task)
        
        # 2: loop over all analysis
        cur_analysis_time = args.start_analysis_time
        while cur_analysis_time <= args.end_analysis_time:
            cur_stats_dir = os.path.join(cur_met_dir, 
                                         cur_analysis_time.strftime('%y%m%d%H'))
            
            # 3: loop over all forecasts (at different valid times)
            for cur_lead_h in range(1, int(args.forecast_length)+1):
                cur_valid_time = cur_analysis_time + timedelta(seconds=cur_lead_h*3600)
                
                # 4: lopp over all asked scores (defined in the task_list, e.g., cur_scores: score1, score2 etc.)
                for cur_score in task_list.keys():
                    # 4.1 extract information from task_list
                    cur_score_name = task_list[cur_score]['score_name']                 # cur_score_name: mae, rmse etc.
                    cur_score_type = task_list[cur_score]['score_type']                 # score_type: cnt, cts etc.
                    
                    # 4.2 get the met output filepath
                    cur_stats_filename = get_stats_filename(args, cur_valid_time, 
                                                            cur_model,
                                                            args.met_task,
                                                            cur_score_type,
                                                            cur_lead_h)
                    cur_stats_path = os.path.join(cur_stats_dir, cur_stats_filename)
                    
                    # 4.3 start writing output
                    
                    # 4.3.1: loop over all asked fields (e.g., T2, U10)
                    for cur_field in args.plot_field_list: # e.g., T2
                        # 4.3.2: extract the score values
                        if not os.path.exists(cur_stats_path):
                            cur_field_value = cur_field_upper_value = cur_field_lower_value = numpy.NaN
                        else:
                            cur_field_value, cur_field_upper_value, cur_field_lower_value = \
                                            read_cnt_cts_stats(args, cur_score, cur_stats_path, cur_score_name, cur_field)
                        
                        # 4.3.3: write outputs
                        stats_output = write_stats_output(stats_output, 'cur_model', cur_model)
                        stats_output = write_stats_output(stats_output, 'cur_score', cur_score)
                        stats_output = write_stats_output(stats_output, 'cur_field', cur_field)
                        stats_output = write_stats_output(stats_output, 'analysis_time', cur_analysis_time.strftime('%Y%m%d%H'))
                        stats_output = write_stats_output(stats_output, 'valid_time', cur_valid_time.strftime('%Y%m%d%H'))
                        stats_output = write_stats_output(stats_output, 'score_value', cur_field_value)
                        stats_output = write_stats_output(stats_output, cur_field + '_upper', cur_field_upper_value)
                        stats_output = write_stats_output(stats_output, cur_field + '_lower', cur_field_lower_value)
                        
            cur_analysis_time = cur_analysis_time + \
                timedelta(seconds = 3600*int(args.analysis_time_interval))
    
    return stats_output

def extract_value_from_stats_output(stats_output, cur_score, cur_model, cur_valid_time, cur_analysis_time,
                                    cur_field):

    cur_score_index = [i for i, x in enumerate(stats_output['cur_score']) if x == cur_score]
    cur_model_index = [i for i, x in enumerate(stats_output['cur_model']) if x == cur_model]
    cur_valid_time_index = [i for i, x in enumerate(stats_output['valid_time']) if x == cur_valid_time]
    cur_analysis_time_index = [i for i, x in enumerate(stats_output['analysis_time']) if x == cur_analysis_time]
    cur_field_index = [i for i, x in enumerate(stats_output['cur_field']) if x == cur_field]
    
    
    score_value_list = list(set(cur_score_index) & set(cur_model_index) & set(cur_valid_time_index) & \
        set(cur_analysis_time_index) & set(cur_field_index))
    
    if len(score_value_list) > 1:
        raise Exception ('mutiple values for one score found, quit')
    else:
        score_value = stats_output['score_value'][score_value_list[0]]
    
    return score_value

def plot_score(args, stats_output):
    """plot the skill score from stats_output"""
    x_axis_label = []
    is_all_nan = lambda L: not len(filter(lambda e: not e is numpy.nan, L))

    fig_width = 10
    fig_hight = 8

    cur_valid_time = args.start_analysis_time + timedelta(seconds=3600)
    while cur_valid_time <= args.end_analysis_time + timedelta(seconds=int(args.forecast_length)*3600):
        x_axis_label.append(cur_valid_time.strftime('%Y%m%d%H'))
        cur_valid_time = cur_valid_time + timedelta(seconds = 3600)

    for cur_plot_field in args.plot_field_list:
        for cur_score in task_list.keys():
            fig_filename = cur_plot_field + '_' + task_list[cur_score]['score_name'] + '.png'
            plt.figure(figsize=(fig_width, fig_hight))
            for cur_model in args.model_list:
                cur_analysis_time = args.start_analysis_time
                while cur_analysis_time <= args.end_analysis_time:
                    score_value_list = []
                    valid_x_index = []
                    cur_analysis_time_str = cur_analysis_time.strftime('%Y%m%d%H')
                    for cur_lead_h in range(1, int(args.forecast_length)+1):
                        cur_valid_time = cur_analysis_time + timedelta(seconds=cur_lead_h*3600)
                        cur_valid_time_str = cur_valid_time.strftime('%Y%m%d%H')

                        cur_valid_x_index = x_axis_label.index(cur_valid_time_str)
                        valid_x_index.append(cur_valid_x_index)

                        score_value = extract_value_from_stats_output(stats_output, cur_score, cur_model,
                                                                      cur_valid_time_str, cur_analysis_time_str,
                                                                      cur_plot_field)
                        score_value_list.append(score_value)

                    if not is_all_nan(score_value_list):
                        plt.plot(valid_x_index, score_value_list, label='{}\n{}'.format(cur_model, cur_analysis_time_str))

                    cur_analysis_time = cur_analysis_time + \
                        timedelta(seconds = 3600*int(args.analysis_time_interval))

            plt.suptitle(cur_plot_field + ', ' + task_list[cur_score]['score_name'])
            plt.grid()
            plt.legend(loc='upper left',bbox_to_anchor=(1,0.5), fontsize = 'small')
            xtick_number = int(max(round(len(score_value_list)/6), 1.0))
            plt.xticks(range(0, len(score_value_list), xtick_number), x_axis_label[0:-1:xtick_number])
            plt.ylabel('skill score')
            plt.savefig(fig_filename, bbox_inches='tight')
            plt.close()

