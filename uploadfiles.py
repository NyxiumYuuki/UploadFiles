"""
https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-uploading-files.html
https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3.html?highlight=Threads%20are%20used%20by%20default
http://ls.pwd.io/2013/06/parallel-s3-uploads-using-boto-and-threads-in-python/
"""
import sys
from os import listdir
from boto.s3.connection import S3Connection
import threading


# args needed to launch the program 
#   aws_key
#   aws_secret_key
#   folder_path

def get_filenames(folder_path):
  return listdir(folder_path)

def main():
  get_filenames("")


if __name__ == "__main__":
  main()
