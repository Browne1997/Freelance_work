#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 22 19:13:58 2023

@author: erin
"""
# Import packages 
#import gdal 
# or rom osgeo import gdal
import math 
import pandas as pd 
import numpy as np
import pyproj

'''-----------------------------'''
# Using a for loop iterate over matched.csv and biggle.csv and apply following calculations
try:
    matched_images = M=pd.read_csv('/home/erin/Desktop/Free_Lance_Projects/Sol_GPS_coords/GPS_worktodate/CSVs-FlightLogs/matched.csv')  
    img_pixcoords = I= pd.read_csv('/home/erin/Desktop/Free_Lance_Projects/Sol_GPS_coords/drone_data/pixelcoords_biigle/12495_csv_image_annotation_report/12495-aldfg-real-data.csv')
except FileNotFoundError:
    matched_images = M=pd.read_csv('/home/djch/Erin_B/Thai/CSVs-FlightLogs/matched.csv')  
    img_pixcoords = I= pd.read_csv('/home/djch/Erin_B/Thai/12495-aldfg-real-data.csv')

matched_cols = matched_images.columns # list of columns
print(matched_cols)
# Camera information is taken via exif of image in pre-csv_build and if not is hard coded here
new_fields = {'focal_length':0.01027,
              'im_width': 5472,
              'im_height': 3648,
              'sh': 0.0088}
new_cols = matched_cols.tolist() # change to python list in order for reindex f(x) to work
for new_col, new_val in new_fields.items():   
    if new_col not in matched_cols:
        new_cols.append(new_col)
        matched_images = matched_images.reindex(new_cols, fill_value = new_val, axis = 'columns')
#print(matched_images.columns)
''' Calculating altitutdes above sea-level - geoid (25.7meters for thailand)
separation CHECK WHICH HE BELIEVES IS THE CORRECT COLUMN '''

M = matched_images
last_keys = None

def process_1(x, M, geod):
    """x in the BIIGLE list of targets
    M is the matched image set

    return a new Series for computed values
    """
    global last_keys
    
    our_image = O = M.loc[M['matched_image'] == x['filename']]
    print(f"{our_image=}")

    if our_image.empty:         # need all returned Series to be same shape, so cheat
        print(f">>>>>EMPTY - {x['filename']}")
        return pd.Series(len(last_keys) * [0.0,] , index=last_keys)  # NB GSD cannot be 0, so look for this...
        
    thing_x, thing_y = eval(x['points'])

    # HACK ATTACK - pandas somehow wants to remember where data came from
    # and print this in the CSV...
    # hence redundant int() and float() below
    
    centre_x = int(O['im_width']//2)
    centre_y = int(O['im_height']//2)  # as ints

    new_d = { 'offset_x' : (dx := thing_x-centre_x),
              'offset_y' : (dy := thing_y-centre_y),
              'filename' : x['filename'],
             }
    new_d['GSD'] = GSD =  float(O['altitude_above_seaLevel(feet)'] * 0.3048 * O['sh'] / \
        (O['focal_length'] * O['im_height']))

    new_d['dist'] = d = math.hypot(dx, dy)
    new_d['bear.deg'] = bearing = float((math.degrees(math.atan2(dy, dx)) + O['gimbal_heading(degrees)']) % 360.0)
    new_d['dist.km'] = (dist_m := d * GSD)/1000.0 # [m to km]

    LONG, LAT, _ = geod.fwd(O['longitude'], O['latitude'], bearing, dist_m, radians=False)

    new_d['True.Longitude'], new_d['True.Latitude'] = float(LONG), float(LAT)

    if last_keys is None:
        last_keys = new_d.keys()
    return pd.Series(new_d.values(), index=new_d.keys())

# B is a bit on the way

B = I.apply(process_1, args=(M, pyproj.Geod(ellps='WGS84')),axis=1)
print(B.iloc[0])
B.to_csv("B.csv", index=False)
