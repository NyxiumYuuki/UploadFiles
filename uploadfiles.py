"""
https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-uploading-files.html
https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3.html?highlight=Threads%20are%20used%20by%20default
http://ls.pwd.io/2013/06/parallel-s3-uploads-using-boto-and-threads-in-python/
https://gist.github.com/arthuralvim/356795612606326f08d99c6cd375f796
https://www.gormanalysis.com/blog/connecting-to-aws-s3-with-python/
"""
import logging, argparse, sys, os
import boto3
import botocore
import threading
import queue


def get_filenames(folder_path):
    filenames = []
    for path, subdirs, files in os.walk(folder_path):
        for name in files:
            filenames.append(os.path.join(path, name))
    return filenames, len(filenames)


def upload(FILENAME):

    s3 = boto3.resource(
        service_name='s3',
        region_name=REGION_NAME,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )
    try:
        s3.Bucket(BUCKET_NAME).upload_file(Filename=FILENAME, Key=FILENAME)
    except botocore.exceptions.ClientError as error:
        logging.error(error)
        sys.exit(4)
    return 0


def worker():
    while True:
        item = q.get()
        if item is None:
            break
        upload(item)
        q.task_done()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Upload files from path to AWS S3 Bucket with threads')
    parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')
    required.add_argument('-p', '--path', help='Path of folder to upload (default: .)', default='.', required=True)
    required.add_argument('-b', '--bucket', help='Bucket name (default: None)', default=None, required=True)
    optional.add_argument('-r', '--region', help='AWS S3 Bucket Region (default: eu-west-3)', default='eu-west-3')
    optional.add_argument('-t', '--threads', help='Number of Threads (default: 20)', default=20)
    optional.add_argument('-y', '-Y', help='Confirm path (default: False)', default=False, action='store_true')

    optional.add_argument('-d', '--debug', help='Debug mode (default: False)', default=False, action='store_true')
    optional.add_argument('-i', '--info', help='Info mode (default: False)', default=False, action='store_true')
    try:
        args = parser.parse_args()
    except argparse.ArgumentError as error:
        logging.error('Catching an argumentError {}'.format(error))

    if args.debug:
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    elif args.info:
        logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    else:
        logging.basicConfig(stream=sys.stderr, level=logging.ERROR)

    AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY', default=None)

    AWS_ACCESS_KEY = 'AKIA4HHPH6LQIDIOIEQI'                                             # TODO	Remove
    if AWS_ACCESS_KEY is None:
        logging.error('No AWS_ACCESS_KEY in Sys Env Variables')
        sys.exit(1)
    # TODO	Verify keys regex
    else:
        logging.info('AWS_ACCESS_KEY found')

    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', default=None)

    AWS_SECRET_ACCESS_KEY = 'Q0cL/ojm3k65mILBhoFDyV9Wr7vKIB/LDfYqu1qJ'                  # TODO	Remove
    if AWS_SECRET_ACCESS_KEY is None:
        logging.error('No AWS_SECRET_ACCESS_KEY in Sys Env Variables')
        sys.exit(2)
    # TODO	Verify keys regex
    else:
        logging.info('AWS_SECRET_ACCESS_KEY found')

    logging.debug('AWS_ACCESS_KEY : %s ', AWS_ACCESS_KEY)
    logging.debug('AWS_SECRET_ACCESS_KEY : %s', AWS_SECRET_ACCESS_KEY)
    logging.info('Path : %s', args.path)
    logging.info('Region : %s', args.region)
    logging.info('Bucket : %s', args.bucket)
    logging.info('Threads : %s', args.threads)
    logging.info('Confirm Y : %s', args.y)

    PATH = args.path
    REGION_NAME = args.region
    BUCKET_NAME = args.bucket
    NB_THREADS = args.threads
    CONFIRM = args.y

    filenames, nbfiles = get_filenames(PATH)
    logging.info('Number of files found in "{}" : {}'.format(args.path, nbfiles))
    while CONFIRM is False:
        CONFIRM = input('Please confirm the path and files to upload, press Y : ')
        if CONFIRM != 'Y':
            CONFIRM = False

    logging.info('Create Boto3 Session')
    s3 = boto3.resource(
        service_name='s3',
        region_name=REGION_NAME,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )
    logging.info(s3)
    logging.info('Buckets found %d', len(list(s3.buckets.all())))
    for bucket in s3.buckets.all():
        try:
            logging.info('  - %s', bucket.name)
        except botocore.exceptions.ClientError as error:
            logging.error(error)
            sys.exit(3)
    logging.info('Upload %s to %s', filenames[0], BUCKET_NAME)
    try:
        s3.Bucket(BUCKET_NAME).upload_file(Filename=filenames[0], Key=filenames[0])
    except botocore.exceptions.ClientError as error:
        logging.error(error)
        sys.exit(4)
    logging.info('Upload success')

    q = queue.Queue()
    threads = []

    for i in range(NB_THREADS):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)

    for filename in filenames:
        q.put(filename)

    q.join()
    for i in range(NB_THREADS):
        q.put(None)
    for t in threads:
        t.join()
    exit(0)