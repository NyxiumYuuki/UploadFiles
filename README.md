# UploadFiles
UploadFiles with Threads for AWS S3 Buckets

0. Download the zip & extract the project
1. Install needed libraries : `pip install -r requirements.txt`
2. Set environnement variables : 
  - `set AWSAccessKeyId=YOUR_AWS_ACCESS_KEY_HERE` & `set AWSSecretKey=YOUR_AWS_SECRET_KEY_HERE` 
    - (`set` for Windows & `export` for Linux)
  - On Windows, you might need to reboot your computer. Don't forget to restart your shell. 
  - Check if the environnement variables are stored.
    - On Windows powershell : `echo $Env:AWSAccessKeyId` & `echo $Env:AWSSecretKey`
    - On Linux shell : `echo $AWSAccessKeyId` & `echo $AWSSecretKey`
5. Run the script `python uploadfiles.py -p PATH_HERE -b S3_BUCKET_NAME_HERE -r AWS_S3_REGION_HERE`
6. Check optional arguments if needed
```
usage: uploadfiles.py [-h] -p PATH -b BUCKET [-r REGION] [-db] [-t THREADS] [-y] [-i] [-d]
Upload files from path to AWS S3 Bucket with threads
required arguments:
  -p PATH, --path PATH  Path of folder to upload (default: .)
  -b BUCKET, --bucket BUCKET
                        Bucket name (default: None)

optional arguments:
  -r REGION, --region REGION
                        AWS S3 Bucket Region (default: eu-west-3)
  -db, --disable_boto3  Use of boto3 S3Transfer threads and not another threads algorithms created from scratch (default: True)
  -t THREADS, --threads THREADS
                        Number of Threads (default: 20)
  -y, --yes             Confirm path (default: False)
  -i, --info            Info mode (default: True)
  -d, --debug           Debug mode (default: False)
```
