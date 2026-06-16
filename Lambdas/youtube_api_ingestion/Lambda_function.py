import logging
import boto3
import os
import json
from datetime import datetime, timezone
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode


#----------------------- Set up logging ------------------#
logger = logging.getLogger()
logger.setLevel(logging.INFO)

#----------------------- AWS Clients ------------------#
s3_client = boto3.client("s3")
s3_sns = boto3.client("sns")


#----------------------- Configuration ------------------#
BRONZE_BUCKET = os.environ.get("S3_BUCKET_BRONZE",  "")
SNS_TOPIC = os.environ.get("SNS_ALERT_TOPIC_ARN", "")
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY", "")
REGIONS = os.environ.get("YOUTUBE_REGIONS", "US,GB,CA,DE,FR,IN,JP,KR,MX,RU").split(",")
API_BASE = "https://www.googleapis.com/youtube/v3/videoCategories"
MAX_RESULTS = 50

def send_alert(subject: str,message: str):
    if SNS_TOPIC:
        try:
            s3_sns.publish(TopicARN=SNS_TOPIC, Subject=subject[:100], Message=message)
            logger.info("Alert sent Successfully")
        except Exception as e:
            logger.error(f"Error sending alert: {e}")
    else:
        logger.warning("SNS_TOPIC not configured, cannot send alert")

def fetch_trending_videos(region: str)-> dict:
    params = urlencode({
        "part": "snippet",
        "chart": "mostPopular",
        "regionCode": region,
        "key": YOUTUBE_API_KEY,
        "maxResults": MAX_RESULTS
    })

    url = f"{API_BASE}/videos?{params}"

    req = Request(url, headers={"Accept": "application/json"})
    with urlopen(req, timeout = 30) as response:
        data = json.loads(response.read().decode("utf-8"))
        return data
    
def fetch_video_categories(region:str) -> dict:
    params = urlencode({
        "part": "snippet",
        "regionCode": region,
        "key": YOUTUBE_API_KEY
    })

    url = f"{API_BASE}/videoCategories?{params}"
    req = Request(url, headers={"Accept": "application/json"})

    with urlopen(req, timeout=30) as response:
        data = json.loads(response.read().decode("utf-8"))
        return data

def write_to_s3(data: dict, bucket:str, key:str):
    body = json.dumps(data, ensure_ascii=False, indent=2)
    response = s3_client.put_object(
        Bucket=bucket,
        Key=key,
        Body=body.encode("utf-8"),
        ContentType="application/json",
        Metadata={
            "source": "youtube_data_api_v3",
            "ingestion_time": datetime.now(timezone.utc).isoformat()
        }
    )
    logger.info(f"Data written to S3: s3://{bucket}/{key}")
    return response

def send_alert(subject:str, message:str):
    if SNS_TOPIC:
        try:
            s3_sns.publish(TopicARN= SNS_TOPIC, Subject=subject[:100], Message=message)
            logger.info("Alert sent successfully")
        except Exception as e:
            logger.error(f"Error sending alert: {e}")
    else:
        logger.warning("SNS_TOPIC not configured, cannot send alert")

def lambda_handler(event, context):
    now = datetime.now(timezone.utc)
    date_partition = now.strftime("%Y-%m-%d")
    hour_partition = now.strftime("%H")
    ingestion_id = now.strftime("%Y%m%d_%H%M%S")

    Results = {"success": [], "failed": []}

    for region in REGIONS:
        # Fetch Trending Videos
        try:
            trending_data = fetch_trending_videos(region)
            vdo_count = len(trending_data.get("items", []))

            trending_data["metadata"] = {
                "ingestion_id": ingestion_id,
                "region": region,
                "ingestion_timestamp": now.isoformat(),
                "video_count": vdo_count,
                "source": "youtube_data_api_v3"
            }
            s3_key = (
                f"youtube/raw_statistics/"
                f"region={region}/"
                f"partition_date={date_partition}/"
                f"partition_hour={hour_partition}/"
                f"{ingestion_id}.json"
            )

            write_to_s3(trending_data, BRONZE_BUCKET, s3_key)
            logger.info(f"Trending videos for region {region} ingested successfully.")

        except (HTTPError,URLError) as e:
            logger.error(f"Error fetching trending videos for region {region}: {e}")
            Results["failed"].append({"region": region, "type": "trending_vidoes", "error": str(e)})
            continue
        except Exception as e:
            logger.error(f"Unexpected error for region {region}: {e}")
            Results["failed"].append({"region": region, "type": "trending_videos", "error": str(e)})
            continue

        # Fetch Video Categories
        try:
            categories_data = fetch_video_categories(region)

            categories_data["metadata"] = {
                "ingestion_id": ingestion_id,
                "region": region,
                "ingestion_timestamp": now.isoformat(),
                "source": "youtube_data_api_v3"
            }

            ref_key = (
                f"youtube/raw_statistics_reference_data/"
                f"region={region}/"
                f"partition_date={date_partition}/"
                f"{region}category_id.json"
            )

            write_to_s3(categories_data, BRONZE_BUCKET, ref_key)
            logger.info(f"Video categories for region {region} ingested successfully.") 

        except (HTTPError,URLError) as e:
            logger.error(f"Error fetching video categories for region {region}: {e}")
            Results["failed"].append({"region": region, "type": "video_categories", "error": str(e)})
            continue

        Results["success"].append(region)

    summary_message = (
        f"Ingestion {ingestion_id} completed,"
        f"success : {len(Results["success"])}/{len(REGIONS)} regions"
        f"failed : {len(Results["failed"])}"
    )

    logger.info(summary_message)

    if Results["failed"]:
        send_alert(
            subject=f"[YT Pipeline] Ingestion partial failure — {ingestion_id}",
            message=json.dumps(Results, indent=2),
        )

    return {
        "statusCode": 200,
        "ingestion_id": ingestion_id,
        "results": Results,
    }


