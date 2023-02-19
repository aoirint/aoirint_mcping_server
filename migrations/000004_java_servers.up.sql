CREATE TABLE "java_servers" (
  "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  "name" TEXT NOT NULL,
  "host" TEXT NOT NULL,
  "port" INTEGER NOT NULL,
  "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER refresh_java_servers_updated_at_step1
  BEFORE UPDATE ON "java_servers" FOR EACH ROW
  EXECUTE PROCEDURE refresh_updated_at_step1();
CREATE TRIGGER refresh_java_servers_updated_at_step2
  BEFORE UPDATE OF "updated_at" ON "java_servers" FOR EACH ROW
  EXECUTE PROCEDURE refresh_updated_at_step2();
CREATE TRIGGER refresh_java_servers_updated_at_step3
  BEFORE UPDATE ON "java_servers" FOR EACH ROW
  EXECUTE PROCEDURE refresh_updated_at_step3();
