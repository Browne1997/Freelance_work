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
    matched_images = M=pd.read_csv('matched.csv')  
    img_pixcoords = I= pd.read_csv('14223-kt-s.csv')
except FileNotFoundError:
    matched_images = M=pd.read_csv('/IGNORE/matched.csv')  
    img_pixcoords = I= pd.read_csv('/IGNORE/12495-aldfg-real-data.csv')

matched_cols = matched_images.columns # list of columns
print(matched_cols)
# Camera information is taken via exif of image in pre-csv_build and if not is hard coded here
new_fields = {'focal_length(mm)'    :'513/50',
              'image_width(pixels)' : 5472,
              'image_height(pixels)': 3648,
              'sh'                  : 0.0088}  # m total vertical height of sensor (m)

new_cols = matched_cols.tolist() # change to python list in order for reindex f(x) to work

for new_col, new_val in new_fields.items():   
    if new_col not in matched_cols:
        print(f"Using default for {new_col}={new_val}")
        new_cols.append(new_col)
        matched_images = matched_images.reindex(new_cols, fill_value = new_val, axis = 'columns')
#print(matched_images.columns)

M = matched_images
# Just in case thee first images don't match, this is the current set of keys
last_keys = ['offset_x', 'offset_y', 'filename', 'GSD', 'dist', 'bear.deg', 'dist.km', 'True.Longitude', 'True.Latitude']
keys_seen = False

def process_1(x, M, geod):
    """x in the BIIGLE list of targets
    M is the matched image set

    return a new Series for computed values
    """
    global last_keys, keys_seen
    
    our_image = O = M.loc[M['matched_image'] == x['filename']]
    #print(f"{our_image=}")

    if our_image.empty:         # need all returned Series to be same shape, so cheat
        print(f">>>>>EMPTY - {x['filename']}")
        return pd.Series(len(last_keys) * [0.0,] , index=last_keys)  # NB GSD cannot be 0, so look for this...
        
    thing_x, thing_y = eval(x['points'])

    # HACK ATTACK - pandas gives us len=1 Series not just strings and numbers
    # and prints this in the CSV...
    # hence redundant int() and float() below - for string use values[]
    
    centre_x = int(O['image_width(pixels)']//2)
    centre_y = int(O['image_height(pixels)']//2)  # as ints

    new_d = { 'offset_x' : (dx := thing_x-centre_x),
              'offset_y' : (dy := thing_y-centre_y),
              'filename' : x['filename'],
             }
    #print(O['focal_length(mm)'].values[0])
    # focal_length is a rational...  values gets just the 513/50 string
    new_d['GSD'] = GSD =  float(O['altitude_above_seaLevel(feet)'] * 0.3048 * O['sh'] / \
        (eval(O['focal_length(mm)'].values[0]) /1000.0 * O['image_height(pixels)']))

    new_d['dist'] = d = math.hypot(dx, dy)
    new_d['bear.deg'] = bearing = float((math.degrees(math.atan2(dy, dx)) + O['gimbal_heading(degrees)']) % 360.0)
    new_d['dist.km'] = (dist_m := d * GSD)/1000.0 # [m to km]

    LONG, LAT, _ = geod.fwd(O['longitude'], O['latitude'], bearing, dist_m, radians=False)

    new_d['True.Longitude'], new_d['True.Latitude'] = float(LONG), float(LAT)

    if not keys_seen:
        assert len(last_keys) == len(new_d.keys())
        last_keys = new_d.keys()
        keys_seen = True
        #print(f"last_keys is {len(last_keys)} \n{last_keys}")
        
    return pd.Series(new_d.values(), index=new_d.keys())

# B is a new DataFrame with just the new calculated stuff and the filename

B = I.apply(process_1, args=(M, pyproj.Geod(ellps='WGS84')),axis=1)  # use the ellipsoid from WGS84
#print(B.iloc[0])
B.to_csv("B.csv", index=False)

# Want one line per annotation with all the matched information
# Can't use isin type merge - this only generates one line from M per matched file in B
# and there can be several annotations per frame

# merge how='inner' is the database inner join - as many rows as there in B, as long as the filename matches
M.merge(B, left_on = 'matched_image', right_on = 'filename', how='inner').to_csv('Final.csv', index=False)

# I is the BIIGLE data, so add on the computed locations
# join() joins columns on the end - and we can't have duplicates

B = B.drop(columns='filename')
new_I = I.join(B)
new_I.to_csv("Biigle_plus.csv", index=False)
