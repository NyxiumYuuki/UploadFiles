"""
    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-uploading-files.html
    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3.html?highlight=Threads%20are%20used%20by%20default
    http://ls.pwd.io/2013/06/parallel-s3-uploads-using-boto-and-threads-in-python/
    https://gist.github.com/arthuralvim/356795612606326f08d99c6cd375f796
    https://www.gormanalysis.com/blog/connecting-to-aws-s3-with-python/
    https://aws.amazon.com/fr/blogs/security/a-safer-way-to-distribute-aws-credentials-to-ec2/
"""
import logging, argparse, sys, os
import boto3
import botocore
import threading
import queue
import re
from boto3.s3.transfer import TransferConfig


class ProgressPercentage(object):

    def __init__(self, filepath, filename, current_nb_file, total_nb_files):
        self._filename = filename
        self._filepath = filepath
        self._current_nb_file = current_nb_file
        self._total_nb_files = total_nb_files
        self._size = float(os.path.getsize(filepath))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(
                "\r[%d/%d] %s  %s / %s  (%.2f%%)" % (
                    self._current_nb_file,
                    self._total_nb_files,
                    self._filename,
                    self._seen_so_far,
                    self._size,
                    percentage))
            sys.stdout.flush()


def run_fast_scandir(dir):  # dir: str, ext: list
    subfolders, files = [], []

    for f in os.scandir(dir):
        if f.is_dir():
            subfolders.append(f.path)
        if f.is_file():
            files.append(f.path)

    for dir in list(subfolders):
        sf, f = run_fast_scandir(dir)
        subfolders.extend(sf)
        files.extend(f)
    return subfolders, files


def upload(filepath, filename, current_nb_file, total_nb_files):
    s3 = boto3.resource(
        service_name='s3',
        region_name=REGION_NAME,
        aws_access_key_id=AWSAccessKeyId,
        aws_secret_access_key=AWSSecretKey
    )
    try:
        s3.Bucket(BUCKET_NAME).upload_file(Filename=filepath, Key=filename,
                                           Callback=ProgressPercentage(filepath, filename, current_nb_file,
                                                                       total_nb_files))
    except botocore.exceptions.ClientError as error:
        logging.error(error)
        sys.exit(4)
    return True


def worker():
    while True:
        filepath, filename, current_nb_file, total_nb_files = q.get()
        if filepath is None or filename is None or current_nb_file is None or total_nb_files is None:
            break
        if upload(filepath, filename, current_nb_file, total_nb_files):
            q.task_done()
        else:
            logging.error('Task error for %s [%d/%d]', filepath, current_nb_file, total_nb_files)
            sys.exit(5)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Upload files from path to AWS S3 Bucket with threads')
    parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')
    required.add_argument('-p', '--path', help='Path of folder to upload (default: .)', default='.', required=True)
    required.add_argument('-b', '--bucket', help='Bucket name (default: None)', default=None, required=True)
    optional.add_argument('-r', '--region', help='AWS S3 Bucket Region (default: eu-west-3)', default='eu-west-3')
    optional.add_argument('-db', '--disable_boto3',
                          help='Use of boto3 S3Transfer threads and not another threads algorithms created from '
                               'scratch (default: True)',
                          default=True, action='store_false')
    optional.add_argument('-t', '--threads', help='Number of Threads (default: 20)', default=20)
    optional.add_argument('-y', '--yes', help='Confirm path (default: False)', default=False, action='store_true')

    optional.add_argument('-i', '--info', help='Info mode (default: True)', default=True, action='store_false')
    optional.add_argument('-d', '--debug', help='Debug mode (default: False)', default=False, action='store_true')

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

    pattern_AWSAccessKeyId = r"(?<![A-Z0-9])[A-Z0-9]{20}(?![A-Z0-9])"
    pattern_AWSSecretKey = r"(?<![A-Za-z0-9/+=])[A-Za-z0-9/+=]{40}(?![A-Za-z0-9/+=])"

    AWSAccessKeyId = os.getenv('AWSAccessKeyId', default=None)
    if AWSAccessKeyId is None:
        logging.error('No AWSAccessKeyId in Sys Env Variables')
        sys.exit(1)
    elif re.match(pattern_AWSAccessKeyId, AWSAccessKeyId) is False:
        logging.error('AWSAccessKeyId Incorrect Pattern, it should be "%s"', pattern_AWSAccessKeyId)
        sys.exit(10)
    else:
        logging.info('AWSAccessKeyId found')

    AWSSecretKey = os.getenv('AWSSecretKey', default=None)
    if AWSSecretKey is None:
        logging.error('No AWSSecretKey in Sys Env Variables')
        sys.exit(2)
    elif re.match(pattern_AWSSecretKey, AWSSecretKey) is False:
        logging.error('AWSSecretKey Incorrect Pattern, it should be "%s"', pattern_AWSSecretKey)
        sys.exit(10)
    else:
        logging.info('AWSSecretKey found')

    logging.debug('AWSAccessKeyId : %s ', AWSAccessKeyId)
    logging.debug('AWSSecretKey : %s', AWSSecretKey)
    logging.info('Path : %s', args.path)
    logging.info('Region : %s', args.region)
    logging.info('Bucket : %s', args.bucket)
    logging.info('Threads : %s', args.threads)
    logging.info('Confirm Y : %s', args.yes)

    PATH = args.path
    REGION_NAME = args.region
    BUCKET_NAME = args.bucket
    NB_THREADS = args.threads
    CONFIRM = args.yes

    subfolders, fullpath = run_fast_scandir(PATH)
    toRemove = PATH.rsplit('/', 1)[0]
    if PATH == toRemove:
        toRemove = PATH.rsplit('\\', 1)[0]
    nbfiles = len(fullpath)
    topath = []
    for path in fullpath:
        topath.append(path.replace(toRemove, ''))
    logging.info('Number of files found in "{}" : {}'.format(args.path, nbfiles))
    while CONFIRM is False:
        CONFIRM = input('Please confirm the path and files to upload, press Y : ')
        if CONFIRM != 'Y':
            CONFIRM = False
    logging.info('Create Boto3 Session')
    s3 = boto3.resource(
        service_name='s3',
        region_name=REGION_NAME,
        aws_access_key_id=AWSAccessKeyId,
        aws_secret_access_key=AWSSecretKey
    )
    logging.info(s3)
    logging.info('Buckets found %d', len(list(s3.buckets.all())))
    for bucket in s3.buckets.all():
        try:
            logging.info('  - %s', bucket.name)
        except botocore.exceptions.ClientError as error:
            logging.error(error)
            sys.exit(3)

    if args.disable_boto3 is False:
        logging.info('Boto3 S3Transfer disable - Use of another Threads algorithm')
        logging.info('Creating queue')
        q = queue.Queue()
        threads = []

        logging.info('Start %d workers threads', NB_THREADS)
        for i in range(NB_THREADS):
            t = threading.Thread(target=worker)
            t.start()
            threads.append(t)

        logging.info('Starting to upload %d files in %s S3 bucket', nbfiles, BUCKET_NAME)
        for i in range(0, nbfiles):
            q.put((fullpath[i], topath[i], i, nbfiles))

        logging.info('Block util all tasks are done')
        q.join()
        logging.info('Stopping workers')
        for i in range(NB_THREADS):
            q.put((None, None, None, None))
        for t in threads:
            t.join()
    else:
        logging.info('Boto3 S3Transfer')
        transfer_config = TransferConfig(max_concurrency=NB_THREADS)
        logging.info('Starting to upload %d files in %s S3 bucket', nbfiles, BUCKET_NAME)
        for i in range(0, nbfiles):
            s3.Bucket(BUCKET_NAME).upload_file(Filename=fullpath[i], Key=topath[i], Config=transfer_config,
                                               Callback=ProgressPercentage(fullpath[i], topath[i], i, nbfiles))
    logging.info('Finished')
    exit(0)
