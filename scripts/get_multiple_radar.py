from datetime import datetime, timedelta
import subprocess
import os

start_radar_datetime_str = '201802191800'
end_radar_datetime_str = '201802201800'
output = '/home/szhang/data/radar/new'
radar_field = 'accumulation'
model_path = '/home/szhang/Downloads/wrf_hourly_nz8kmN-NCEP-obsnudge-39_d02_2018-02-20_03_00_00'
start_radar_datetime = datetime.strptime(
                            start_radar_datetime_str, '%Y%m%d%H%M')
end_radar_datetime = datetime.strptime(
                            end_radar_datetime_str, '%Y%m%d%H%M')

cur_radar_datetime = start_radar_datetime

while cur_radar_datetime <= end_radar_datetime:
    print cur_radar_datetime
    rad_cmd = ('get_and_decode_radar.py -t {} -d {} '
               '--download-data --produce_cappi --rad2mod '
               '--radar_field {} '
               '--model_path {} '
               '--plot_radar').format(
                    cur_radar_datetime.strftime('%Y%m%d%H%M'), 
                    output, radar_field,
                    model_path)
 
    print rad_cmd              
    p1 = subprocess.Popen(rad_cmd, cwd=os.getcwd(), shell=True)
    p1.wait()
    cur_radar_datetime = cur_radar_datetime + timedelta(seconds=3600)
