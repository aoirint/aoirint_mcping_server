DROP INDEX "java_ping_records__created_at__index";
DROP INDEX "java_ping_records__java_server_id__index";

DROP TRIGGER refresh_java_ping_records_updated_at_step1 ON "java_ping_records";
DROP TRIGGER refresh_java_ping_records_updated_at_step2 ON "java_ping_records";
DROP TRIGGER refresh_java_ping_records_updated_at_step3 ON "java_ping_records";

DROP TABLE "java_ping_records";
