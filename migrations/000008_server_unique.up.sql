ALTER TABLE "bedrock_servers" ADD CONSTRAINT "bedrock_servers__host__port__unique" UNIQUE("host", "port");
ALTER TABLE "java_servers" ADD CONSTRAINT "java_servers__host__port__unique" UNIQUE("host", "port");
