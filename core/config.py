import os
from dotenv import load_dotenv
load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "neo4j://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")

APP_SECRET = os.getenv("APP_SECRET", "change_me")

RUN_WITH_DOCKER = os.getenv("RUN_WITH_DOCKER", "0") == "1"
NEO4J_DOCKER_CONTAINER = os.getenv("NEO4J_DOCKER_CONTAINER", "neo4j-mgmt")
NEO4J_DOCKER_HTTP_PORT = int(os.getenv("NEO4J_DOCKER_HTTP_PORT", "7474"))
NEO4J_DOCKER_BOLT_PORT = int(os.getenv("NEO4J_DOCKER_BOLT_PORT", "7687"))
NEO4J_DOCKER_PASSWORD = os.getenv("NEO4J_DOCKER_PASSWORD", "neo4j_password_change_me")
