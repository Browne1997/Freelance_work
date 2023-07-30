# Sol_work: Converting x,y pixel coords to GPS coords

## Step 1: Upload images to AWS server and upload to BIIGLE project folder
This allows images to be uploaded to BIIGLE without requiring a BIIGLE paid account (as it doesn't require us to save our data with them).

Login details for AWS account is:  
  Root email: erinbrowne97@gmail.com  
  Password: WolfFish23.  
  
IAM policy  
  Access key: AKIAQSTZCHP4VM7ODWFA

Login detail for BIIGLE account is:  
  Access to this has been sent via email. I would suggest setting up your own if you no longer want me to have access post-project.   
  Root email: erinbrowne97@gmail.com
  Password: Harley1997.

Instructions to do this is in the BIIGLE presentation. Including, how to create label trees and create the x,y pixel coords of ALDFG (and annoations when required). It also explains how to extract the biigle.csv with the x,y coords to be converted to GPS coords using the image name as an identifier to the flight/image metadata (final step). 

## Step 2: Building exif package for python locally

Using bash terminal (a.k.a requires bash installation and python version => 3.8.10) build new version of exifread. This step was done as exifread standard package could not read maker notes in the image metadata required to create initial algorithm to match flight metadata with image metadata.

Follow these steps to build in bash terminal window:
> git clone https://github.com/g8sqh/exifread.git  
(OR Download the exif-py folder in this repo)  
> cd exifread/  
> git switch -c develop origin/develop   
> python -m pip install rdflib  
> python -m pip install .  

NOTE I HAVE DONE THESE STEPS NOT IN A VIRTUAL ENV - If you have any worries or setups already on your computer you are scared of breaking I would install Anaconda and create an virtual env and install pkgs via this method (mainly ensures that multiple versions of python won't fight with eachother).

## Step 3: Create one large csv for flight metadata in timeseries order 

Run csv_merge.py on local directory of flight metadata csv's - making sure to change filepath within the code to your relevant local directories (line 12 - ignore line 14). 
> python (or python3 dependant on how you name it in the installation) csv_merge.py  

This code is used in the algorithm built in pre-csv_build.py and the output should be big.csv

## Step 4: Create pre-csv's required for doing the GPS conversions

The algorithm built is based on a sub-set of data -1.6GB provided (however code is appropriate to run over all data). The paths in line 48 and 49 will again need changed to local directory paths for these images and the big.csv generated from step 2.
> python (or python3 dependant on how you name it in the installtion) pre_csv_build.py

The output will generate a csv called matched.csv - this is used as the pre-csv for the final code to generate GPS coords. The csv extracts all image names mapping them to their flight metadata as well as extracting GPS and bearing from image metadata. These are matched based on closest similarities on timestamps, lat/long, bearing, gimbal and flight positions in this order. The algorithm took this approach to best match images to the correct metadata whilst reducing errors as timestamps between camera, onboard GPS and ground station GPS caused data matching issues.

## Step 5: Create post-csv's of converted GPS coords 

Direct conversions of R code to python.

> python (or python3 dependant on how you name it in the installtion) post_csv_build.py
