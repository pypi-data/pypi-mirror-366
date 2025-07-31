import os
import boto3
import progressbar


def upload_file(bucket, file_name, remote_path):
    print("Uploading: ", file_name)
    
    statinfo = os.stat(file_name)

    up_progress = progressbar.progressbar.ProgressBar(maxval=statinfo.st_size)
    #tmp['max'] = statinfo.st_size
    
    up_progress.start()

    def upload_progress(chunk):
        #tmp['current'] = up_progress.currval + chunk
        #print("Mine: ", int(tmp['current']/tmp['max']*100), "   ")
        # tmp['prog'].update(30)
        up_progress.update(up_progress.currval + chunk)

    bucket.upload_file(file_name, remote_path.replace("\\", "/"), Callback=upload_progress)

    up_progress.finish()

def upload_s3(bucket, local_path, remote_path):
    if os.path.isfile(local_path):  
        bucket.upload_file(local_path, "/".join(remote_path.split("/")[1:]))
        print(local_path)
    else:
        try:
            for path, subdirs, files in os.walk(local_path):
                for file in files:
                    dest_path = path.replace(local_path,"")
                    __s3file = os.path.normpath(remote_path + "/" + dest_path + "/" + file)
                    __local_file = os.path.join(path, file)
                    
                    upload_file(bucket, file_name=__local_file, remote_path=__s3file)
                    yield 1
        except Exception as e:
            print(" ... Failed!! Quitting upload!!")
            print(e)
            raise e



def count_files(path):
    count = 0
    for base, dirs, files in os.walk(path):
        count = count + len(files)    
    return count



def count_files_minio(bucket, prefix):
    count=0
    for obj in bucket.objects.filter(Prefix=prefix):
        count+=1
    return count


def upload_folder(minio_address, minio_access_key, minio_secret_key, bucket_name, local_path, remote_path):

    s3 = boto3.resource('s3', 
        endpoint_url = minio_address,
        aws_access_key_id = minio_access_key, 
        aws_secret_access_key = minio_secret_key
        )
    
    n_of_files = count_files(local_path)

    bucket = s3.Bucket(bucket_name)

    count = 0
    for result in upload_s3(bucket, local_path, remote_path):
        count += result
        yield count, n_of_files


def folder_exists(minio_address, minio_access_key, minio_secret_key, bucket_name, path):
    s3 = boto3.resource('s3', 
        endpoint_url = minio_address,
        aws_access_key_id = minio_access_key, 
        aws_secret_access_key = minio_secret_key
        )
    bucket = s3.Bucket(bucket_name)
    
    if sum(1 for _ in bucket.objects.filter(Prefix=path)) > 0:
        return True
    else:
        return False

def minio_connection_is_working(minio_address, minio_access_key, minio_secret_key, bucket_name):
    s3 = boto3.resource('s3', 
        endpoint_url = minio_address,
        aws_access_key_id = minio_access_key, 
        aws_secret_access_key = minio_secret_key
        )
    bucket = s3.Bucket(bucket_name)

    if bucket.creation_date:
        return True
    else:
        return False

def isfile_s3(bucket, key: str) -> bool:
    """Returns T/F whether the file exists."""
    objs = list(bucket.objects.filter(Prefix=key))
    return len(objs) == 1 and objs[0].key == key


def download_s3(minio_address, minio_access_key, minio_secret_key, bucket_name, remote_path, local_path):
    s3 = boto3.resource('s3', 
        endpoint_url = minio_address,
        aws_access_key_id = minio_access_key, 
        aws_secret_access_key = minio_secret_key
        )
    bucket = s3.Bucket(bucket_name)

    if isfile_s3(bucket, remote_path):
        bucket.download_file(remote_path, local_path)
    else:
        try:
            for obj in bucket.objects.filter(Prefix=remote_path):
                target = obj.key if local_path is None \
                    else os.path.join(local_path, os.path.relpath(obj.key, remote_path))
                if not os.path.exists(os.path.dirname(target)):
                    os.makedirs(os.path.dirname(target))
                if obj.key[-1] == '/':
                    continue
                bucket.download_file(obj.key, target)
                yield 1
        except Exception as e:
            print(" ... Failed!! Quitting download!!")
            print(e)
            raise e


def download_folder(minio_address, minio_access_key, minio_secret_key, bucket_name, local_path, remote_path):

    s3 = boto3.resource('s3', 
            endpoint_url = minio_address,
            aws_access_key_id = minio_access_key, 
            aws_secret_access_key = minio_secret_key
            )
    bucket = s3.Bucket(bucket_name)

    n_of_files = count_files_minio(bucket, remote_path)

    count = 0
    for result in download_s3(bucket_name=bucket_name, local_path=local_path, minio_access_key=minio_access_key, minio_secret_key=minio_secret_key, minio_address=minio_address, remote_path=remote_path):
        count += result
        yield count, n_of_files
