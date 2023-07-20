"""
merge a set of csv files, sorted by time and marked for origin
"""

import csv
from pathlib import Path
from collections import deque 
from exifread import process_file # note the exifread package has been build and needs special installation
from datetime import datetime, timedelta

if False:
    all_flights = Path(r"/home/erin/Desktop/Free_Lance_Projects/Sol_GPS_coords/drone_data/SolNets_flightdata/CSVs-FlightLogs/").glob('KP_*.csv')
else:
    all_flights = Path(r"/home/djch/Erin_B/Thai/CSVs-FlightLogs").glob('KP_*.csv')


all_csvs = []

for num_csvs, f in enumerate(all_flights):
   for row in csv.DictReader(f.open(newline = '')):
      if not row['datetime(utc)'].strip():
         continue
      
      row['orig_filename'] = fn = str(f.name)
      row['matched_image'] = ''

      all_csvs.append(row)


print(f"Got {len(all_csvs)} from {num_csvs} csvs")

all_csvs.sort(key=lambda x : datetime.strptime(x['datetime(utc)'], '%Y-%m-%d %H:%M:%S'))

print("Sorted")

with open(f.parent / 'big.csv', 'w', newline='') as csvfile:
   writer = csv.DictWriter(csvfile, fieldnames=row.keys())

   writer.writeheader()
   for r in all_csvs:
      writer.writerow(r)
