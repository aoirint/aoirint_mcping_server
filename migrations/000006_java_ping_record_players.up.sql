CREATE TABLE "java_ping_record_players" (
  "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  "java_ping_record_id" UUID NOT NULL REFERENCES "java_ping_records"("id") ON DELETE CASCADE,
  "player_id" TEXT NOT NULL,
  "name" TEXT NOT NULL,
  "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER refresh_java_ping_record_players_updated_at_step1
  BEFORE UPDATE ON "java_ping_record_players" FOR EACH ROW
  EXECUTE PROCEDURE refresh_updated_at_step1();
CREATE TRIGGER refresh_java_ping_record_players_updated_at_step2
  BEFORE UPDATE OF "updated_at" ON "java_ping_record_players" FOR EACH ROW
  EXECUTE PROCEDURE refresh_updated_at_step2();
CREATE TRIGGER refresh_java_ping_record_players_updated_at_step3
  BEFORE UPDATE ON "java_ping_record_players" FOR EACH ROW
  EXECUTE PROCEDURE refresh_updated_at_step3();

CREATE INDEX "java_ping_record_players__java_ping_record_id__index"
  ON "java_ping_record_players" 
  USING btree
  ("java_ping_record_id");

CREATE INDEX "java_ping_record_players__created_at__index"
  ON "java_ping_record_players" 
  USING btree
  ("created_at");
