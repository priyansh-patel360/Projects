#import boto3
import pandas as pd
import os
#from  credential import *
''' 

session = boto3.Session(
   # aws_access_key_id=aws_access_key_id,
   # aws_secret_access_key=aws_secret_access_key
)


S3 = session.resource("s3")
s3_client = session.client("s3")

response = s3_client.list_buckets()

#print(response['Buckets'])

for bkt in response['Buckets']:
    print(bkt['Name'])
print('\n')


# to create a bucket.
CreateBucket = s3_client.create_bucket(Bucket='priyansh-ap-northeast-yt-datapipeline-scripts',CreateBucketConfiguration={'LocationConstraint': 'ap-northeast-3'})



with open('test.txt', 'w') as f:
    f.write('This is a test file for AWS S3 upload')
    f.close()

with open('test.txt', 'rb') as f:   
    s3_client.upload_fileobj(f, 'priyansh-ap-northeast-3-test-bucket', 'test.txt')

response = s3_client.list_buckets()

#print(response['Buckets'])

for bkt in response['Buckets']:
    print(bkt['Name'])

'''
print(os.getcwd())
file_path = 'Streaming_platform_Data_Pipeline/Data1/CA_category_id.json'
with open(file_path, 'r', encoding='utf-8') as f:
    data = f.read()
    print(data)

df =pd.json_normalize(data.get("kind"))
print(df)