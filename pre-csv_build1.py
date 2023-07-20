#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 30 13:37:39 2023

@author: erin
"""

import csv, pickle
#import warnings
from pathlib import Path
from collections import deque 
from exifread import process_file # note the exifread package has been build and needs special installation
from datetime import datetime, timedelta 

# EXTRACT INFORMATION FROM IMAGE METADATA 
# Static dictionary of name in column headings to match to exif - EXSISTS
exif_csv_tags = {'XMP GimbalRollDegree':    'gimbal_roll(degrees)', # XMP read the exif data that is hidden my the drone maker 
                'XMP GimbalYawDegree'  :    'gimbal_heading(degrees)',
                'XMP GimbalPitchDegree':    'gimbal_pitch(degrees)',
                'XMP FlightRollDegree' :    ' roll(degrees)',  # YES - they have leading spaces on some columns
                'XMP FlightYawDegree'  :    ' compass_heading(degrees)',
                'XMP FlightPitchDegree':    ' pitch(degrees)',
                'GPS GPSLatitude'      :    'latitude',
                'GPS GPSLongitude'     :    'longitude',
                'EXIF DateTimeOriginal':    'datetime(utc)'}
# Adding useful new tags to flight data csv
exif_csv_newtags = {#'FieldOfView'                   :  'field_of_view(degrees)',
                    'EXIF ExifImageWidth'                :  'image_width(pixels)',
                    'EXIF ExifImageLength'               :  'image_height(pixels)',
                    'EXIF FocalLength'                    :  'focal_length(mm)',
                    'EXIF DigitalZoomRatio'              :  'digitial_zoom_ratio'}

# Constructing new mapping dictionary from the columns in flightdata.csv's to be matched to exif form image metadata
csv_exif_tags = dict((v,k) for(k,v) in exif_csv_tags.items())
# Change Path according to local directory paths. Deque allows edit list from both ends (front and back or e.g. start and end csv)

def path_key(x:Path):
    part1 = orig = str(x.name)[6:]
    #print(part1, part1[9])
    if part1[9] == 'S':         # yy-mm-dd-S?_####  or yy-mm-dd_####
        part1 = part1[:8] + part1[11:]
        print(f"fixed {orig=} to {part1}")

    return part1

if False:
    all_flights = Path(r"/home/erin/Desktop/Free_Lance_Projects/Sol_GPS_coords/drone_data/SolNets_flightdata/CSVs-FlightLogs/big.csv")
    all_images = Path("/home/erin/Desktop/Free_Lance_Projects/Sol_GPS_coords/drone_data/Sol's Nets/").glob('*.JPG')
else:
    all_flights = Path(r"/home/djch/Erin_B/Thai/CSVs-FlightLogs/big.csv")
    all_images = Path("/home/djch/Erin_B/Thai/Sol_s Nets").glob('*.JPG')

    
# Function to turn GPS degree,mins,secs to decimal degrees
def dms2degrees(l):
    d,m,s = l.values # check its a 3 element list 
    return d.decimal() + m.decimal()/60.0 + s.decimal()/3600.0
    
def process_1_exif(name, show_keys=False):
    #with warnings.catch_warnings():
    #    warnings.filterwarnings("ignore", message="does not look a valid")
    with name.open('rb') as f:
        exif = process_file(f, show_keys) 
        exif['_file_name'] = name
        print(f">> {f.name}")
        
    for tag in exif_csv_tags.keys():
        # print(f'{exif.keys() = }') # matching keys in dictionary between flight data to image meta data
        # exif if decoding in raw format 
        if show_keys:
            print(f'{tag= } {exif.get(tag, "missing")}') #getattr matching the exif_csv_tags to the flightdata tags
        if tag == 'EXIF DateTimeOriginal': # turn tags into python objects in order to compare with flight data 
            exif[tag] = new_t =  datetime.strptime(exif[tag].values, '%Y:%m:%d %H:%M:%S') - timedelta(hours = 7) # timedelt accounts for time diff
        elif tag.startswith('GPS '):
            exif[tag] = dms2degrees(exif[tag]) # use above function to convert GPS coords 
        elif tag.startswith('XMP Flight') or tag.startswith('XMP Gimbal'):
            exif[tag] = float(exif[tag])
    return exif


#all_exif = sorted( (process_1_exif(x) for x in all_images), key = lambda x :x['EXIF DateTimeOriginal'])

last_second = None

print("Reading csv")

try:
    with open('big.pickle', 'rb') as f:
    # The protocol version used is detected automatically, so we do not
    # have to specify it.
        csv_rows, time_starts = pickle.load(f)

except FileNotFoundError as e:
    print (f"{e=}")
    csv_rows = []
    time_starts = {}
    
    for csv_row in csv.DictReader(all_flights.open(newline = '')):
        time_str = csv_row['datetime(utc)'].strip()

        if not time_str:            # valid time
            continue

        row_time = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')  
        csv_row['python_dtg'] = row_time  # will be skipped if we write out big.csv (extrasaction = 'ignore')

        if last_second != row_time:
            time_starts[row_time] = len(csv_rows)  # index where we will now store :-)
            last_second = row_time

        csv_rows.append(csv_row)
        
    with open('big.pickle', 'wb') as f:
    # The protocol version used is detected automatically, so we do not
    # have to specify it.
        pickle.dump((csv_rows, time_starts) , f, pickle.HIGHEST_PROTOCOL)

def check_for_gaps(ptr:int):
    """ look fwd and back within expedition for gaps in time
    call at start of second!
    """
    expedition = csv_rows[ptr]['orig_filename']

    t0 =  csv_rows[ptr]['python_dtg']
    p = ptr
    t = t0
    
    period = timedelta(seconds=30)

    this_period = 0
    while (this_dtg := csv_rows[p]['python_dtg']) - t0 < period:
        if  expedition == csv_rows[p]['orig_filename']:
            if this_dtg == t:
                this_period += 1
                last_dtg = this_dtg
            else:                   # new second
                if (jump := this_dtg - t) != timedelta(seconds=1):
                    print(f"TIME JUMP {jump} to {this_dtg}")
                if this_period > 13:
                    breakpoint()
                elif this_period >= 11:
                    print(f"Extra {last_dtg} {this_period}")
                elif this_period == 10:
                    pass
                elif this_period >=8:
                    print(f"Few missing {last_dtg} {this_period}")
                else:
                    print(f"LOTS missing {last_dtg} {this_period}")
                t = this_dtg
                last_dtg = this_dtg
                this_period = 1
        p += 1

    this_period = 0
    p = ptr-1
    t = t0 - timedelta(seconds=1)  # start the previous second, even if it isn't in the record...
    last_dtg = t                   # for missing previous second
    while t0 -(this_dtg := csv_rows[p]['python_dtg']) <  period:
        if  expedition == csv_rows[p]['orig_filename']:
            if this_dtg == t:
                this_period += 1
                last_dtg = this_dtg
            else:                   # new second
                if (jump := this_dtg - t) != -timedelta(seconds=1):
                    print(f"TIME JUMP BACKWARDS {-jump} to {this_dtg}")
                if this_period > 13:
                    breakpoint()
                elif this_period >= 11:
                    print(f"Extra {last_dtg} {this_period}")
                elif this_period > 10:
                    breakpoint()
                elif this_period == 10:
                    pass
                elif this_period >=8:
                    print(f"- Few missing {last_dtg} {this_period}")
                else:
                    print(f"- LOTS missing {last_dtg} {this_period}")
                t = this_dtg
                last_dtg = this_dtg
                this_period = 1
        p -= 1

LOOK_BACK = 30

FLIGHT_KEYS = list((exif_csv_tags[x], x) for x in exif_csv_tags.keys() if x.startswith('XMP '))
DODGY_KEYS = {'gimbal_roll(degrees)' : 0.5,
              }

def score_flight(trial, ref_exif):
    err = 0
    for k, k_ref in FLIGHT_KEYS:
        
        try:
            exif_val = ref_exif[k_ref]
            if 'Yaw' in k_ref and exif_val < 0.0:
                exif_val += 360.0
            err += DODGY_KEYS.get(k, 1.0) * abs(exif_val - float(trial[k]))  # keys in the exif are floated on input
        except KeyError:
            print(f"{k=} {k_ref=} {list(ref_exif.keys())} {list(trial.keys())}")
            raise
    return err

# Read and pull exif data from image JPGs
our_time = None

# strategy more complex now all_flights contains a mixture of expeditions
# auxiliary table indexes time to offset in all_flights (for first at that second)
# scan forward for a decent match - we overshoot to be sure we get a decent one. This identifies the original csv (and hence expedition)
# go backwards (that expedition) to find gimbal/flight match, and also photo = 1 within reasonable distance

ok_match = good_match = poor_match = location_fail = 0
unknown_times = []

for image_num, exif in enumerate(process_1_exif(x, show_keys=False) for x in all_images):
    location_error = motion_error = 0.0
    last_location_error = None

    our_time = exif['EXIF DateTimeOriginal']
    print(f'\n{exif["_file_name"] =} @ {our_time}')
    
    # Coarse match - same time as ours

    try:
        start_offset = time_starts[our_time]
        print(f"Second found at {start_offset}")
    except KeyError:
        print("Photo time UNKNOWN!!!")
        unknown_times.append(our_time)
        continue

    # Finer match - match by location

    expedition = None
    location_ptr = start_offset

    search_delta = timedelta(seconds=25)

    lp0 = location_ptr
    for mult in (1.0, 2.0, 4.0, 8.0,16.0):
        location_ptr = lp0

        if mult != 1.0:
            print(f"Search failed: broaden to {mult} times normal")
            
        while (csv_row := csv_rows[location_ptr])['python_dtg'] <= our_time + search_delta:  # believe we'll match within the second
            location_error = 0.0 
            for tag in exif_csv_tags.keys():
                if tag.startswith('GPS '):
                    # Take tag GPS name and look up in exif = column heading (flight data spreadsheet), convert to from string to floating point numbers, then subtract from location_error and take absolute value 
                    location_error += abs(exif[tag] - float(csv_row[exif_csv_tags[tag]])) 

            if last_location_error is not None:  # see a decent error recently
                if last_location_error < 1.9*location_error:
                    break
                if location_error < last_location_error:
                    assert  expedition == csv_row['orig_filename'], f"{expedition=} != {csv_row['orig_filename']}" 
                    last_location_error = location_error
                    best_location_ptr = location_ptr
            elif location_error < (0.7e-7 * mult):
                last_location_error = location_error
                best_location_ptr = location_ptr
                expedition = csv_row['orig_filename']
            elif False or location_error > 12e-3:
                #print(f"SKIPPING {location_error=} @ {location_ptr} {csv_row['orig_filename']} {exif['GPS GPSLatitude']=} {exif['GPS GPSLongitude']=}")
                pass
                #break
            location_ptr += 1
        else:
            if mult == 1.0:
                check_for_gaps(lp0)
            continue
        break                   # out of the for loop
    else:
        print(f"Fallen off the end {search_delta=} after {location_ptr-start_offset} lines")
        #break
        location_fail +=1
        continue

    print(f'good match {best_location_ptr} {last_location_error =} {csv_row["datetime(utc)"]}')
    #print(f'{location_ptr=}')
    #for xx in range(7):
    #    next_row()              # grab two more, more margin for good fit

    def track_expedition(ptr:int, n:int):
        """from ptr, iterate fwd or back a max of n times
        cf range(abs(n)+1)
        
        yields new ptr
        """
        dirn = 1 if n>0 else -1

        i = 0
        n *= dirn
        
        while i <= n:            # left to go
            if csv_rows[ptr]['orig_filename'] == expedition:
                #print((i, ptr))
                yield (i, ptr)
                i += 1
            ptr += dirn
            
    LOOK_BACK = 30
    #location_ptr += 30
    
    for n, i in track_expedition(location_ptr, -LOOK_BACK):  # index backwards for photo
        if csv_rows[i]['isPhoto'] == '1':
            #print(f"Found the nearest photo {n} rows back")
            photo_at = n
            break
    else:
        print("Can't find the photo!!!\nTrying next image")
        break
        continue

    best_err = 1e10
    
    for n, i in track_expedition(location_ptr, -photo_at):  # want to look at the marked line too
        this_err = score_flight(csv_rows[i], exif)
        best_err = min(best_err, this_err)
        if this_err == best_err:
            best_i = i
        if this_err < 0.1:  # data in 0.1 deg resolution, so 'perfect' bar float error
            flight_match_line = i
            print(f"Flight match ({this_err}) at {flight_match_line}, photo_delta {photo_at-n} {expedition=}")
            csv_rows[i]['matched_image'] = exif["_file_name"].name
            good_match += 1
            break
    else:
        print(f"Didn't get a perfect flight match, best was {best_err=} at {best_i}")
        if best_err >0.5:
            print("BAILING: that's not good enough")
            poor_match += 1
        else:
            ok_match += 1
            csv_rows[i]['matched_image'] = exif["_file_name"].name
            #break
    # break 

    if False:
        for tag in exif_csv_newtags.keys():
            #print(f'{exif.keys() = }') # matching keys in dictionary between flight data to image meta data
            #exif if decoding in raw format 
            print(f'{tag= } {exif.get(tag, "missing")}') #getattr matching the exif_csv_tags to the flightdata tags

unknown_times.sort()
image_num += 1                  # 0 based count from enumerate

print(f"FINAL: {image_num=} {good_match=} {ok_match=} {poor_match=} {location_fail=} unknown_times={len(unknown_times)}")
#print('\n'.join(map(str,unknown_times)))

starts = iter(time_starts.keys())
prev_t = next(starts)
this_t = next(starts)

for u in unknown_times:
    if this_t is None:          # we fell off the end
        print(f"<- {u-prev_t} -> {u}")
        continue
    
    if u < prev_t:
        print(f"{u} <- {prev_t-u}") #  {prev_t}")
        continue

    while u > this_t:
        prev_t = this_t
        try:
            this_t = next(starts)
        except StopIteration:
            this_t = None
    print(f"<- {u-prev_t} -> {u} <- {this_t-u} ->")

print("Writing matched csv rows")

with (all_flights.parent / 'matched.csv').open('w', newline='') as f:
    fieldnames = ['first_name', 'last_name']
    writer = csv.DictWriter(f, fieldnames=csv_rows[0].keys(), extrasaction='ignore')

    writer.writeheader()
    writer.writerows(i for i in csv_rows if i['matched_image'])
