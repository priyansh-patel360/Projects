import os
import boto3
import json
import logging
import pandas as pd
from datetime import datetime, timezone
from urllib.parse import unquote_plus
import awswrangler as wr

#----------------------- Set up logging ------------------#
logger = logging.getLogger()
logger.setLevel(logging.INFO)

#----------------------- Configuration ------------------#
SILVER_BUCKET = os.environ["S3_BUCKET_SILVER"]
GLUE_DB_SILVER = os.environ.get("GLUE_DATABASE_SILVER", "yt_pipeline_silver_dev")
GLUE_TABLE = os.environ.get("GLUE_TABLE_SILVER", "clean_ref_data")
SNS_TOPIC = os.environ.get("SNS_ALERT_TOPIC_ARN", "")
SILVER_PATH = f"s3://{SILVER_BUCKET}/youtube/reference_data/"



s3_client = boto3.client("s3")
sns_client = boto3.client("sns")

def read_json_from_s3(bucket: str, key) -> dict:
    try:
        response = s3_client.get_object(Bucket=bucket, key=key)
        content = response['Body'].read().decode('utf-8')
        return json.loads(content)
    except Exception as e:
        logger.error(f"Error reading JSON from S3: {e}")
        raise

def df_validator(df: pd.Dataframe) -> pd.DataFrame:
    if df.empty:
        logger.warning("DataFrame is empty")
        return df


    required_columns = ["id", "snippet.title"]
    actual_columns = df.columns.tolist()
    missing_columns = [col for col in required_columns if col not in actual_columns]
    if missing_columns:
        logger.warning(f"Missing required columns: {missing_columns}")


    before_len = len(df)
    df = df.drop_duplicates(subset="id", keep="last")
    after_len = len(df)
    if before_len != after_len:
        logger.info(f"Removed {before_len - after_len} duplicate rows based on 'id' column")

    return df
def send_alert(subject: str, message: str):
    if SNS_TOPIC:
        try:
            sns_client.publish(TopicArn=SNS_TOPIC, Subject=subject, Message=message)
            logger.info("Alert sent successfully")
        except Exception as e:
            logger.error(f"Error sending alert: {e}")
    else:
        logger.warning("SNS_TOPIC not configured, cannot send alert")

def lambda_handler(event, context):
    records = event.get("Records",[])
    if not records:
        records = [event] if "s3" in event else []
    processed = []
    errors = []
    for record in records:
        bucket=record["s3"]["bucket"]["name"]
        key=unquote_plus(record["s3"]["object"]["key"])
        logger.info(f"Processing file: s3://{bucket}/{key}")
        try:
            raw_data = read_json_from_s3(bucket, key)

            if "items" in raw_data and isinstance(raw_data["items"], list):
                df = pd.json_normalize(raw_data["items"])
                
            else:
                df = pd.json_normalize(raw_data)

            logger.info(f" raw shape: {df.shape}")

            df = df_validator(df)
            # Add metadata columns
            df["ingestion_timestamp"] = datetime.now(timezone.utc).isoformat()
            df["source_file"] = f"s3://{bucket}/{key}"

            region = "unknnown"
            for part in key.split("/"):
                if part.startswith("region="):
                    region = part.split("=")[1]
                    break
            df["region"] = region

            logger.info(f" validated shape: {df.shape}")

            wr_response = wr.s3.to_parquet(
                df=df,
                path=SILVER_PATH,
                dataset=True,
                database=GLUE_DB_SILVER,
                table=GLUE_TABLE,
                partition_cols=["region"],
                mode="overwrite_partitions",
                schema_evolution=True
                )
            
            logger.info(f"  Written to Silver: {SILVER_PATH}")
            processed.append({"key": key, "region": region, "rows": len(df)})

        except Exception as e:
            logger.error(f"Error processing record: {e}", exc_info=True)
            errors.append({"key": key if "key" in dir() else "unknown", "error": str(e)})

    # ── Summary ──────────────────────────────────────────────────────────
    if errors:
        send_alert(
            subject="[YT Pipeline] Silver reference transform failed",
            message=json.dumps(errors, indent=2),
        )

    return {
        "statusCode": 200,
        "processed": processed,
        "errors": errors,
    }