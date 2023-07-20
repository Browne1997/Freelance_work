# Sol_work: Converting x,y pixel coords to GPS coords

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
This code is used in the algorithm built in pre-csv_build.py and the output should be big.csv

# Step 3: Create pre-csv's required for doing the GPS conversions

The algorithm built is based on a sub-set of data -1.6GB provided (however code is appropriate to run over all data). The paths in line 48 and 49 will again need changed to local directory paths for these images and the big.csv generated from step 2.
> python (or python3 dependant on how you name it in the installtion) csv_merge.py

The output will generate a csv called matched.csv - this is used as the pre-csv for the final code to generate GPS coords. The csv extracts all image names mapping them to their flight metadata as well as extracting GPS and bearing from image metadata. These are matched based on closest similarities on timestamps, lat/long, bearing, gimbal and flight positions in this order. The algorithm took this approach to best match images to the correct metadata whilst reducing errors as timestamps between camera, onboard GPS and ground station GPS caused data matching issues. Some images may not match but will be indicated -

Q- does the code print out image names that don't match so they can note the ones with error?
