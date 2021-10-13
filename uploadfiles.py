"""
https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-uploading-files.html
https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3.html?highlight=Threads%20are%20used%20by%20default
http://ls.pwd.io/2013/06/parallel-s3-uploads-using-boto-and-threads-in-python/
"""
import argparse, sys
import os
import boto3
import threading


def get_filenames(folder_path):
  filenames = []
  for path, subdirs, files in os.walk(folder_path):
    for name in files:
        filenames.append(os.path.join(path, name))
  return filenames, len(filenames)

def main(AWS_KEY, AWS_SECRET_KEY, REGION_NAME, FOLDER_PATH, CONFIRM):
  filenames, nbfiles = get_filenames(FOLDER_PATH)
  while(CONFIRM==None):
    print("Number of files founded : {}".format(nbfiles))
    CONFIRM = input("Please confirm the path and files to upload, press Y")
    if CONFIRM != 'Y':
      CONFIRM = None
  print(filename)
  session = boto3.Session(
      aws_access_key_id=AWS_KEY,
      aws_secret_access_key=AWS_SECRET_KEY,
      region_name=REGION_NAME
  )
  s3 = session.resource('s3')

if __name__ == "__main__":
  #TODO	Verify keys reggex
  AWS_KEY = os.getenv('AWS_KEY', default="test")
  if AWS_KEY == None:
  	print("No AWS_KEY in Sys Env Variables")
  	exit()
  
  AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY', default="test_secret")
  if AWS_SECRET_KEY == None:
  	print("No AWS_SECRET_KEY in Sys Env Variables")
  	exit()
  
  #TODO	Get Sys Args
  parser=argparse.ArgumentParser()
  parser.add_argument('--path', help='Path of folder to upload')
  parser.add_argument('--region', help='AWS region')
  parser.add_argument('-y', help='Confirm path')
  args=parser.parse_args()
  print(args)
  print(sys)
  
  FOLDER_PATH = args.path
  if FOLDER_PATH == None:
  	FOLDER_PATH = "."
  REGION_NAME = args.region
  if REGION_NAME == None:
  	REGION_NAME = "eu-west-3"
  print(FOLDER_PATH, REGION_NAME, args.y)
  main(AWS_KEY, AWS_SECRET_KEY, REGION_NAME, FOLDER_PATH, args.y)
