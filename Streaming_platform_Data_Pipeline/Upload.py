import subprocess
import os

def upload_to_s3(file_name, bucket_name, common_path):
    command = f"aws s3 cp {file_name} s3://{bucket_name}/{common_path}"
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"File '{file_name}' uploaded successfully to 's3://{bucket_name}/{common_path}'")
    except subprocess.CalledProcessError as e:
        print(f"Error uploading file: {e.stderr.decode()}")

print(os.getcwd())
os.chdir("Data1")
print(os.getcwd())
common_path_for_csv = "youtube/raw_statistics/"
common_path_for_json = "youtube/raw_statistics_ref/"
bucket_name = "priyansh-ap-northeast-yt-datapipeline-bronze"
for file in os.listdir(): 
    if file.endswith(".csv"):
        common_path_ext = os.path.splitext(file)[0][:2]
        common_path = f"{common_path_for_csv}region={common_path_ext}/"
        upload_to_s3(file, bucket_name, common_path)
        #print(f"aws s3 cp {file} s3://{bucket_name}/{common_path}")
    
    else:
        common_path_ext = os.path.splitext(file)[0][:2]
        common_path = f"{common_path_for_json}region={common_path_ext}/"
        upload_to_s3(file, bucket_name, common_path)
        #print(f"aws s3 cp {file} s3://{bucket_name}/{common_path}")

