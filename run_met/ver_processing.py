from datetime import datetime, timedelta
import numpy
from netCDF4 import Dataset
from scipy import spatial
import os

# map the real model name to the short one
# (e.g., input: nz8kmN-NCEP, output: NCEP8)
wrfname_map = {
    'nz8kmN-NCEP': 'NCEP8',
    'nz8kmN-NCEP-obsnudge': 'NCEP8n',
    'nz8kmN-NCEP-var': 'NCEP8v',
    'analysis': 'analysis',
    'background': 'background'
    }

verf_field = {
    'T2': {'lat_name': 'XLAT',
           'lon_name': 'XLONG'},
    'TT': {'lat_name': 'XLAT',
           'lon_name': 'XLONG'},
    'RH': {'lat_name': 'XLAT',
           'lon_name': 'XLONG'},
    'U10': {'lat_name': 'XLAT_U',
           'lon_name': 'XLONG_U'},   
    'V10': {'lat_name': 'XLAT_V',
           'lon_name': 'XLONG_V'},          
    'UU': {'lat_name': 'XLAT_U',
           'lon_name': 'XLONG_U'},
    'VV': {'lat_name': 'XLAT_V',
           'lon_name': 'XLONG_V'},
    }

def read_obs_ascii(obs_ascii_file, fcst_datetime, fcst_var):
    '''read the observation in ascii from the start_met application
       all fields (e.g., T2, RH etc.) are read at the same time and
       stored in a list: obs_data_list, which has the elements
                   obs_platform, obs_time, obs_lat, obs_lon, 
                   obs_height, obs_field, obs_value
    '''
    obs_gribcode = {
        'T2': 11,
        'TT': 11,
        'RH': 52,
        'U10': 33,
        'V10':34,
        'UU': 33,
        'VV': 34,
        }
    
    f = open(obs_ascii_file)
    lines = f.readlines()
    obs_data_list = []
    for line in lines:
        filtered_line = filter(None, line.split(' '))
        obs_bufr_type = filtered_line[0]
        obs_platform = filtered_line[1]
        obs_time = datetime.strptime(filtered_line[2], '%Y%m%d_%H%M')
        obs_lat = float(filtered_line[3])
        obs_lon = float(filtered_line[4])
        if obs_lon < 0:
            obs_lon = 360.0 + obs_lon
        obs_height = float(filtered_line[5])
        obs_field = float(filtered_line[6])
        obs_value = float(filtered_line[10])
        
        if (fcst_datetime != obs_time) or (obs_gribcode[fcst_var] != obs_field):
            continue
        
        if obs_value > 999 or obs_value < -999:
            continue
        
        cur_obs = {'obs_platform':obs_platform, 
                   'obs_time': obs_time, 
                   'obs_lat': obs_lat, 
                   'obs_lon': obs_lon, 
                   'obs_height': obs_height,
                   'obs_field': obs_field, 
                   'obs_value': obs_value}
        
        obs_data_list.append(cur_obs)
    
    return obs_data_list


def get_model_value(fcst_file,
                    fcst_var_name,
                    fcst_var_lat_name,
                    fcst_var_lon_name,
                    obs_data_list):
    '''read and process the netcdf forecast file produced by wrf_interp
       (1) it reads the field "fcst_var_name" from "fcst_file"
       (2) go through all the observations corresponding to "fcst_var_name" 
                                    and find the nearest fcst location and value
       (3) attach the fcst info to "obs_data_list", so the elements extend to:
                   obs_platform, obs_time, obs_lat, obs_lon, 
                   obs_height, obs_field, obs_value,
                   fcst_value, fcst_lat, fcst_lon
    '''
    
    # 0: reads the field "fcst_var_name" from "fcst_file" 
    fcst_fid = Dataset(fcst_file, 'r')
    lats = fcst_fid.variables[fcst_var_lat_name][:]  # extract/copy the data
    lons = fcst_fid.variables[fcst_var_lon_name][:]
    var = fcst_fid.variables[fcst_var_name][:]
    
    lons[lons < 0] = 360.0 + lons[lons < 0]
    
    x = lats.shape[1]
    y = lats.shape[2]
    
    # 1: find the latest observation location and get the obs value
    mod_pts_list = []
    mod_ij_list = []
    for i in range(0, x):
        for j in range(0, y):
            cur_pt = [lats[0,i,j], lons[0,i,j]]
            cur_ij = [i, j]
            mod_pts_list.append(cur_pt)
            mod_ij_list.append(cur_ij)
    
    mod_pts = numpy.asarray(mod_pts_list)
    
    fcst_obs_list = []
    for cur_obs in obs_data_list:
        req_obs_latlon = [cur_obs['obs_lat'], cur_obs['obs_lon']]
        closest_model_latlon = mod_pts[spatial.KDTree(mod_pts).query(
            req_obs_latlon)[1]]
        closest_model_dis, closest_model_index = spatial.KDTree(mod_pts).query(
            req_obs_latlon)
        
        closest_model_i = mod_ij_list[closest_model_index][0]
        closest_model_j = mod_ij_list[closest_model_index][1]
        
        if closest_model_dis > 0.1:
            continue
        
        if var.ndim == 4:
            var_value = var[0,0,closest_model_i, closest_model_j]
        elif var.ndim == 3:
            var_value = var[0,closest_model_i, closest_model_j]
            
        print req_obs_latlon, cur_obs['obs_value'], closest_model_latlon, var_value
        cur_obs['fcst_value'] = var_value
        cur_obs['fcst_lat'] = lats[0, closest_model_i, closest_model_j]
        cur_obs['fcst_lon'] = lons[0, closest_model_i, closest_model_j]
        fcst_obs_list.append(cur_obs)
    
    return fcst_obs_list


def write_fcst_obs_list(fcst_obs_list, mod_obs_ascii_path):
    """take the output from fcst_obs_list, and write it out 
       depending on the field, e.g., 
       *T2_17122501.mod_obs:
       verif_time obslat obslon obs fcstlat fcstlon fcst
       2017-12-25 01:00:00 -46.7 168.5 291.1 -46.6 168.5 286.5
       ....
       
       """
    fout = open(mod_obs_ascii_path, "w")
    fcst_obs_line_header = 'verif_time obslat obslon obs fcstlat fcstlon fcst'
    fout.write(fcst_obs_line_header + '\n')
       
    for cur_fcst_obs in fcst_obs_list:
        cur_fcst_obs_line = '{} {} {} {} {} {} {}'.format(
            cur_fcst_obs['obs_time'], 
            cur_fcst_obs['obs_lat'], cur_fcst_obs['obs_lon'], cur_fcst_obs['obs_value'],
            cur_fcst_obs['fcst_lat'], cur_fcst_obs['fcst_lon'], cur_fcst_obs['fcst_value'])
        fout.write(cur_fcst_obs_line + '\n')
    
    fout.close()
    
def setup_ver(args):
    """main control of run_ver
    step1: read the observation file (in ascii) produced by start_met.py
    step2: read the forecast file from wrf_interp
    step3: produce the fcst-obs combined reports
    step4: produce the stats scores and stored in the cnt file
    """
    
    obs_ascii_path = os.path.join(args.pre_download_obs, 'obs_ascii', 'obs_ascii')
    
    cur_analysis_time = args.start_analysis_time
    
    for cur_model in args.model_list:
        while cur_analysis_time <= args.end_analysis_time:
            cur_model_dir = os.path.join(args.pre_download_fcst,
                                              'wp', 
                                              cur_analysis_time.strftime('%y%m%d%H'))
            ver_out_dir = os.path.join(args.work_dir, wrfname_map[cur_model],
                                           'met_dir', 'point_stat',
                                           cur_analysis_time.strftime('%y%m%d%H'))
                
            if not os.path.exists(ver_out_dir):
                os.makedirs(ver_out_dir)
                
            for cur_fcst_h in range(1, int(args.forecast_length) + 1):
                cur_valid_time = cur_analysis_time + timedelta(seconds = 3600*cur_fcst_h)
                cur_model_filename = 'wrf_hourly_{}_d0{}_{}:00:00_INTRP'.format(cur_model,
                                                        args.domain_id,
                                                        cur_valid_time.strftime('%Y-%m-%d_%H'))
                cur_model_path = os.path.join(cur_model_dir, cur_model_filename)
                
                mod_obs_ascii_dir = os.path.join(args.work_dir, wrfname_map[cur_model],
                                                  'mod_obs_ascii',
                                                  cur_analysis_time.strftime('%y%m%d%H'))
                cut_met_dir = os.path.join(args.work_dir, wrfname_map[cur_model],
                                                  'met_dir', 'point_stat',
                                                  cur_analysis_time.strftime('%y%m%d%H'))
    
                cut_cnt_filename = 'point_stat_0{}0000L_{}0000V_cnt.txt'.format(cur_fcst_h,
                                                        cur_valid_time.strftime('%Y%m%d_%H'))

                cut_mpr_filename = 'point_stat_0{}0000L_{}0000V_mpr.txt'.format(cur_fcst_h,
                                                        cur_valid_time.strftime('%Y%m%d_%H'))
                
                cut_cnt_path = os.path.join(cut_met_dir, cut_cnt_filename)
                cut_mpr_path = os.path.join(cut_met_dir, cut_mpr_filename)    
                
                if os.path.exists(cut_cnt_path):
                    os.remove(cut_cnt_path)

                if os.path.exists(cut_mpr_path):
                    os.remove(cut_mpr_path)
                
                cut_cnt_fid = open(cut_cnt_path, "a")
                cnt_header = 'MODEL FCST_LEAD FCST_VALID_BEG FCST_VALID_END OBS_VALID_BEG OBS_VALID_END \
                      FCST_VAR OBS_VAR RMSE RMSE_BCL RMSE_BCU ME ME_BCL ME_BCU MAE MAE_BCL MAE_BCU FCST_THRESH OBS_THRESH \n'

                cut_mpr_fid = open(cut_mpr_path, "a")
                mpr_header = 'MODEL FCST_LEAD FCST_VALID_BEG FCST_VALID_END OBS_VALID_BEG OBS_VALID_END \
                      FCST_VAR OBS_VAR OBS_LAT OBS_LON FCST OBS \n'
                
                cut_cnt_fid.write(cnt_header)
                cut_mpr_fid.write(mpr_header)
    
                if not os.path.exists(mod_obs_ascii_dir):
                    os.makedirs(mod_obs_ascii_dir)
                
                for cur_ver_field in verf_field.keys():
                    cur_lat_name = verf_field[cur_ver_field]['lat_name']
                    cur_lon_name = verf_field[cur_ver_field]['lon_name']
                
                    obs_data_list = read_obs_ascii(obs_ascii_path, cur_valid_time, cur_ver_field)
                    
                    fcst_obs_list = get_model_value(cur_model_path,  cur_ver_field, 
                                                    cur_lat_name, cur_lon_name,
                                                    obs_data_list)
                    mod_obs_ascii_path = os.path.join(mod_obs_ascii_dir,
                                                      cur_ver_field + '_' + \
                                                      cur_valid_time.strftime('%y%m%d%H') + '.mod_obs')
                    write_fcst_obs_list(fcst_obs_list, mod_obs_ascii_path)
                    
                    generate_cnt(cut_cnt_fid, cur_model, mod_obs_ascii_path,
                                 cur_fcst_h, cur_valid_time, cur_ver_field)

                    generate_mpr(cut_mpr_fid, cur_model, mod_obs_ascii_path,
                                 cur_fcst_h, cur_valid_time, cur_ver_field)
                
                cut_cnt_fid.close()
                cut_mpr_fid.close()
                    
            cur_analysis_time = cur_analysis_time + \
                    timedelta(seconds = 3600*int(args.analysis_time_interval))

def generate_mpr(cur_fid, cur_model, mod_obs_ascii_path,
                 cur_fcst_h, cur_valid_time,
                 cur_fcst_var):
    """generate the mpr file (format is similar to the one produce by MET)"""
    with open(mod_obs_ascii_path) as f:
        lines = f.readlines()

    model = cur_model
    fcst_lead = cur_fcst_h
    fcst_valid_beg = cur_valid_time.strftime('%Y%m%d_%H0000')
    fcst_valid_end = fcst_valid_beg
    obs_valid_beg = cur_valid_time.strftime('%Y%m%d_%H0000')
    obs_valid_end = obs_valid_beg
    fcst_var = cur_fcst_var
    obs_var = cur_fcst_var
    for i, line in enumerate(lines):
        if i == 0:
            continue
        obs_lat = float(line.split(' ')[2])
        obs_lon = float(line.split(' ')[3])
        fcst = float(line.split(' ')[7])
        obs = float(line.split(' ')[4])
        cut_mpr_line = '{} {} {} {} {} {} {} {} {} {} {} {}\n'.format(model, fcst_lead,
                            fcst_valid_beg, fcst_valid_end,
                            obs_valid_beg, obs_valid_end,
                            fcst_var, obs_var,
                            obs_lat, obs_lon, fcst, obs)
    
        cur_fid.write(cut_mpr_line)

def generate_cnt(cur_fid, cur_model, mod_obs_ascii_path,
                 cur_fcst_h, cur_valid_time,
                 cur_fcst_var):
    """generate the cnt file (format is similar to the one produce by MET)"""
    with open(mod_obs_ascii_path) as f:
        lines = f.readlines()
    
    model = cur_model
    fcst_lead = cur_fcst_h
    fcst_valid_beg = cur_valid_time.strftime('%Y%m%d_%H0000')
    fcst_valid_end = fcst_valid_beg
    obs_valid_beg = cur_valid_time.strftime('%Y%m%d_%H0000')
    obs_valid_end = obs_valid_beg
    fcst_var = cur_fcst_var
    obs_var = cur_fcst_var
    rmse, rmse_bcl, rmse_bcu = calculate_cnt(lines)
    me = me_bcl = me_bcu = 'NA'
    mae = mae_bcl = mae_bcu = 'NA'
    cut_cnt_line = '{} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} NA NA\n'.format(model, fcst_lead,
                        fcst_valid_beg, fcst_valid_end,
                        obs_valid_beg, obs_valid_end,
                        fcst_var, obs_var,
                        rmse, rmse_bcl, rmse_bcu,
                        me, me_bcl, me_bcu,
                        mae, mae_bcl, mae_bcu)
    
    cur_fid.write(cut_cnt_line)
    
    
def calculate_cnt(lines):
    """calculate RMSE etc."""
    fcst_value_list =[]
    obs_value_list = []
    for i, line in enumerate(lines):
        if i > 0:
            if float(line.split(' ')[4]) == -888888.0:
                continue
            obs_value_list.append(float(line.split(' ')[4]))
            fcst_value_list.append(float(line.split(' ')[-1]))
    
    obs_value = numpy.asarray(obs_value_list)
    fcst_value = numpy.asarray(fcst_value_list)
    
    n = len(fcst_value)
    rmse = numpy.linalg.norm(fcst_value - obs_value)/numpy.sqrt(n)
    rmse_bcl = 'NA'
    rmse_bcu = 'NA' 
    
    return rmse, rmse_bcl, rmse_bcu

