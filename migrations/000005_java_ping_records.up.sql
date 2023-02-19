CREATE TABLE "java_ping_records" (
  "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  "java_server_id" UUID NOT NULL REFERENCES "java_servers"("id") ON DELETE CASCADE,
  "timeout" NUMERIC NOT NULL,
  "is_timeout" BOOLEAN NOT NULL,
  "version_protocol" INTEGER,
  "version_name" TEXT,
  "latency" NUMERIC,
  "players_online" INTEGER,
  "players_max" INTEGER,
  "description" TEXT,
  "favicon" TEXT,
  "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER refresh_java_ping_records_updated_at_step1
  BEFORE UPDATE ON "java_ping_records" FOR EACH ROW
  EXECUTE PROCEDURE refresh_updated_at_step1();
CREATE TRIGGER refresh_java_ping_records_updated_at_step2
  BEFORE UPDATE OF "updated_at" ON "java_ping_records" FOR EACH ROW
  EXECUTE PROCEDURE refresh_updated_at_step2();
CREATE TRIGGER refresh_java_ping_records_updated_at_step3
  BEFORE UPDATE ON "java_ping_records" FOR EACH ROW
  EXECUTE PROCEDURE refresh_updated_at_step3();

CREATE INDEX "java_ping_records__java_server_id__index"
  ON "java_ping_records" 
  USING btree
  ("java_server_id");

CREATE INDEX "java_ping_records__created_at__index"
  ON "java_ping_records" 
  USING btree
  ("created_at");
