bucket Name = priyansh-ap-northeast-3
Test Bucket Name = priyansh-ap-northeast-3-test-bucket
Bronze Bucket Name = priyansh-ap-northeast-yt-datapipeline-bronze
Silver bucket Name = priyansh-ap-northeast-yt-datapipeline-silver
Gold Bucket Name = priyansh-ap-northeast-yt-datapipeline-gold
Scripts bucket Name = priyansh-ap-northeast-yt-datapipeline-scripts
Athena query result bucket = priyansh-ap-northeast-yt-datapipeline-athena-glue-query-result

sns arn = arn:aws:sns:ap-northeast-3:811267951262:yt-datapipeline-alerts-dev:c13193fb-37b4-4bef-8e95-56dc745a62af

# Gold layer

--gold_database : yt-pipeline-gold-dev
--gold_bucket : priyansh-ap-northeast-yt-datapipeline-gold
--silver_database : yt-pipeline-silver-dev
