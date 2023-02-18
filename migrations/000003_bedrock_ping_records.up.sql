CREATE TABLE "bedrock_ping_records" (
  "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  "bedrock_server_id" UUID NOT NULL REFERENCES "bedrock_servers"("id") ON DELETE CASCADE,
  "timeout" NUMERIC NOT NULL,
  "is_timeout" BOOLEAN NOT NULL,
  "version_protocol" INTEGER,
  "version_brand" TEXT,
  "version_version" TEXT,
  "latency" NUMERIC,
  "players_online" INTEGER,
  "players_max" INTEGER,
  "motd" TEXT,
  "map" TEXT,
  "gamemode" TEXT,
  "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER refresh_bedrock_ping_records_updated_at_step1
  BEFORE UPDATE ON "bedrock_ping_records" FOR EACH ROW
  EXECUTE PROCEDURE refresh_updated_at_step1();
CREATE TRIGGER refresh_bedrock_ping_records_updated_at_step2
  BEFORE UPDATE OF "updated_at" ON "bedrock_ping_records" FOR EACH ROW
  EXECUTE PROCEDURE refresh_updated_at_step2();
CREATE TRIGGER refresh_bedrock_ping_records_updated_at_step3
  BEFORE UPDATE ON "bedrock_ping_records" FOR EACH ROW
  EXECUTE PROCEDURE refresh_updated_at_step3();

CREATE INDEX "bedrock_ping_records__bedrock_server_id__index"
  ON "bedrock_ping_records" 
  USING btree
  ("bedrock_server_id");

CREATE INDEX "bedrock_ping_records__created_at__index"
  ON "bedrock_ping_records" 
  USING btree
  ("created_at");
