import os
from datetime import datetime, timedelta

def ascii2nc(obsproc_dir, ascii2nc_dir,
                 met_installation, ascii2nc_config):
    f_obs_ascii = os.path.join(obsproc_dir, "obs_ascii")
    f_ascii2nc = os.path.join(ascii2nc_dir, "obs_ascii.nc")
    ascii2nc_exe = os.path.join(met_installation, 'bin', 'ascii2nc')
    ascii2nc_cmd = '{} {} {} -config {}'.format(ascii2nc_exe, f_obs_ascii, f_ascii2nc, ascii2nc_config)
    os.system(ascii2nc_cmd)

def obsproc2ascii(obs_ascii_dir, obsproc_data, processed_list):
    """all output from obsproc is written in one ascii file""" 
    obs_field = ['obs_temp', 'obs_speed', 'obs_direction', 'obs_dewp', 'obs_humidity']
    
    obs_type = {
        'FM-12': 'ADPSFC'
        }
    
    obs_height = {
        'FM-12': {'obs_temp': 2.0,
                  'obs_humidity': 2.0,
                  'obs_dewp': 2.0,
                  'obs_speed': 10.0,
                  'obs_direction': 10.0}
        }
    
    # https://rda.ucar.edu/docs/formats/grib/gribdoc/params.html
    obs_gribcode = {
        'obs_temp': 11,
        'obs_humidity': 52,
        'obs_dewp': 17,
        'obs_speed': 32,
        'obs_direction': 31
        }

    f_obs_ascii_log = open(os.path.join(obs_ascii_dir, "obs_ascii_log"), "w")
    
    f_obs_ascii_log.write('processed obsproc file: {}\n'.format(len(processed_list)))
    for obsproc_file in processed_list:
        f_obs_ascii_log.write('     {}\n'.format(obsproc_file))
    f_obs_ascii_log.close()
    
    f_obs_ascii = open(os.path.join(obs_ascii_dir, "obs_ascii"), "w")
    for cobstype in obs_field:
        cobs_gribcode = obs_gribcode[cobstype]
        for cdata in obsproc_data:
            cobs_height = obs_height[cdata['obs_platform']][cobstype]
            cobs_type = obs_type[cdata['obs_platform']]
                                 
            message_type = cobs_type
            stn_id = cdata['obs_id']
            valid_time = cdata['obs_datetime'][0:4] + cdata['obs_datetime'][5:7] + \
                        cdata['obs_datetime'][8:10] + '_' + cdata['obs_datetime'][11:13] + \
                        cdata['obs_datetime'][14:16]
            lat = cdata['obs_lat']
            lon = cdata['obs_lon']
            elevation = cobs_height
            grib_code = cobs_gribcode
            level = cdata['obs_pressure']
            height = cobs_height
            qc_string = '0'
            obs_value = cdata[cobstype]
                               
            point_obs_line = '{} {} {} {} {} {} {} {} {} {} {}\n'.format(
                message_type, stn_id, valid_time, lat, lon, elevation, grib_code,
                level, height, qc_string, obs_value)
            
            f_obs_ascii.write(point_obs_line)
    
    f_obs_ascii.close()
        

def get_obsproc_obs(args, obsproc_dir):
    processed_list = []
    cur_analysis_time = args.start_analysis_time
    
    obs_data = [] 
    while cur_analysis_time <= (args.end_analysis_time + 
                                timedelta(seconds = int(args.forecast_length)*3600.0)):
        cur_obsproc_filename = 'obs_gts_{}.3DVAR'.format(cur_analysis_time.strftime('%Y-%m-%d_%H:%M:%S'))
        
        obs_obsproc_path = os.path.join(obsproc_dir, cur_obsproc_filename)
        
        if (os.path.exists(obs_obsproc_path)) and \
                not ((obs_obsproc_path in processed_list)):
            processed_list.append(obs_obsproc_path)
            data_start = False
            with open(obs_obsproc_path, "r") as ins:
                for line in ins:
                    if '#-------' in line:
                        data_start = True
                        continue
                    if data_start:
                        filtered_line = filter(None, line.split(' '))
                        
                        # obs header
                        if filtered_line[0].startswith('FM'):
                            obs_platform = filtered_line[0]
                            obs_datetime = filtered_line[1]
                            obs_lat = filtered_line[4]
                            obs_lon = filtered_line[5]
                            obs_id = filtered_line[7]
                        else:
                            # obs body
                            if len(filtered_line) == 21:
                                obs_pressure = filtered_line[0]
                                obs_speed = filtered_line[3]
                                obs_direction = filtered_line[6]
                                obs_height = filtered_line[9]
                                obs_temp = filtered_line[12]
                                obs_dewp = filtered_line[15]
                                obs_humidity = filtered_line[18]
                                cobs_dict = {
                                    'obs_platform': obs_platform,
                                    'obs_datetime': obs_datetime,
                                    'obs_lat': obs_lat,
                                    'obs_lon': obs_lon,
                                    'obs_id': obs_id,
                                    'obs_pressure': obs_pressure,
                                    'obs_speed': obs_speed,
                                    'obs_direction': obs_direction,
                                    'obs_height': obs_height,
                                    'obs_temp': obs_temp,
                                    'obs_dewp': obs_dewp,
                                    'obs_humidity': obs_humidity}
                                obs_data.append(cobs_dict)
        
        cur_analysis_time = cur_analysis_time + \
                timedelta(seconds = 3600*int(args.analysis_time_interval))
        
    return obs_data, processed_list
        