# Sol_work: Converting x,y pixel coords to GPS coords
'>' indicates a line of code to run
# Step 1: Building exif package for python locally

Using bash terminal (a.k.a requires bash installation and python version => 3.8.10) build new version of exifread. This step was done as exifread standard package could not read maker notes in the image metadata required for extraction of X data to create initial algorithm to match flight metadata with image metadata.

Follow these steps to build in bash terminal windows:
> git clone https://github.com/g8sqh/exifread.git
OR
Download the exif-py folder in this repo
> cd exifread/
> git switch -c develop origin/develop 
> python -m pip install rdflib
> python -m pip install .

# Step 2: Create one large csv for flight metadata in timeseries order 

Run csv_merge.py on local directory of flight metadata csv's - making sure to change filepath within the code to your relevant local directories (line 12 - ignore line 14). 
> python (or python3 dependant on how you name it in the installtion) csv_merge.py
This code is used in the algorithm built in pre-csv_build.py.

# Step 3: Create pre-csv's required for doing the GPS conversions

The algorithm built is based on a sub-set of data -1.6GB provided (however code is appropriate to run over all data). The paths in line 48 and 49 will again need changed to local directory paths for these images and the big.csv generated from step 2.
> python (or python3 dependant on how you name it in the installtion) csv_merge.py
