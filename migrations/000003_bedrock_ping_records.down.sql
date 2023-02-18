DROP INDEX "bedrock_ping_records__created_at__index";
DROP INDEX "bedrock_ping_records__bedrock_server_id__index";

DROP TRIGGER refresh_bedrock_ping_records_updated_at_step1 ON "bedrock_ping_records";
DROP TRIGGER refresh_bedrock_ping_records_updated_at_step2 ON "bedrock_ping_records";
DROP TRIGGER refresh_bedrock_ping_records_updated_at_step3 ON "bedrock_ping_records";

DROP TABLE "bedrock_ping_records";
