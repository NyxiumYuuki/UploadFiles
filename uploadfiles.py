"""
https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-uploading-files.html
https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3.html?highlight=Threads%20are%20used%20by%20default
http://ls.pwd.io/2013/06/parallel-s3-uploads-using-boto-and-threads-in-python/
"""
import sys
import os
#from boto.s3.connection import S3Connection
#import threading


# args needed to launch the program 
#   aws_key
#   aws_secret_key
#   folder_path

def get_filenames(folder_path):
  filenames = []
  for path, subdirs, files in os.walk(folder_path):
    for name in files:
        filenames.append(os.path.join(path, name))
  return filenames

def main(AWS_KEY, AWS_SECRET_KEY, FOLDER_PATH):
  print(os.getcwd())
  filenames = get_filenames(FOLDER_PATH)
  print(filenames)


if __name__ == "__main__":
  # TODO	Get Sys Args for variable
  AWS_KEY = ""
  AWS_SECRET_KEY = ""
  FOLDER_PATH = "test/"
  main(AWS_KEY, AWS_SECRET_KEY, FOLDER_PATH)
