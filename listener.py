from minio import Minio
import os
import logging
from urllib3.exceptions import ReadTimeoutError
import subprocess

S3_BUCKET_NAME='ggbn'

# Map the file name to the directory
file_dir_map = {
    "NHMO-BI.zip": "/srv/ipt/resources/birds/source/",
    "NHMO-DAR.zip": "/srv/ipt/resources/o_dna_arthropods/source/",
    "NHMO-DFH.zip": "/srv/ipt/resources/o_dna_fish_herptiles/source/",
    "O-DFL.zip": "/srv/ipt/resources/o_dna_fungi_lichens/source/",
    "NHMO-DOT.zip": "/srv/ipt/resources/o_dna_other/source/",
    "O-DP.zip": "/srv/ipt/resources/o_dna_plants/source/",
    "NHMO-DMA.zip": "/srv/ipt/resources/o_mammals/source/"
}

def listen():
    logging.info(f"Listening to {os.getenv('S3_HOST')} / {S3_BUCKET_NAME} ...")
    client = Minio(os.getenv('S3_HOST'), access_key=os.getenv('S3_ACCESS_KEY'), secret_key=os.getenv('S3_SECRET_KEY'), secure=False)

    try:
        with client.listen_bucket_notification(S3_BUCKET_NAME, events=["s3:ObjectCreated:*"]) as events:
            for event in events:
                for record in event['Records']:
                    obj = record['s3']['object']
                    object_name = obj['key']
                    if object_name.endswith('.zip') and object_name in file_dir_map:
                        data = client.get_object(S3_BUCKET_NAME, object_name)
                        with open(object_name, 'wb') as file_data:
                            for d in data.stream(32*1024):
                                file_data.write(d)

                        # Move the file to the Samba drive and unzip it
                        subprocess.run(["mv", object_name, file_dir_map[object_name]], check=True)
                        subprocess.run(["unzip", "-o", file_dir_map[object_name] + object_name, "-d", file_dir_map[object_name]], check=True)
    except ReadTimeoutError as e:
        logging.error('Python minio listen_bucket_notification timeout, restarting...')
        listen()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    listen()
