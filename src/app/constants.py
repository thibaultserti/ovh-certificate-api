"""Constants."""

import os

APP_HOST = os.environ.get("APP_HOST", "0.0.0.0")
APP_PORT = os.environ.get("APP_PORT", 8080)


# OVH CONF
OVH_CREDS_PATH = os.getenv("OVH_ENDPOINT", "/tmp/.ovh")

OVH_APPLICATION_KEY = os.getenv("OVH_APPLICATION_KEY")
OVH_APPLICATION_SECRET = os.getenv("OVH_APPLICATION_SECRET")
OVH_CONSUMER_KEY = os.getenv("OVH_CONSUMER_KEY")

DOMAIN_NAME = os.getenv("DOMAIN_NAME")

CERTBOT_STAGING = os.getenv("CERTBOT_STAGING", "False").lower() == "true"
CERTBOT_EMAIL = os.getenv("CERTBOT_EMAIL", f"admin@{DOMAIN_NAME}")
CERTBOT_PROPAGATION_SECONDS = os.getenv("CERTBOT_PROPAGATION_SECONDS", "15")
CERTBOT_WORKDIR = "/tmp/letsencrypt"

UVICORN_WORKER = os.getenv("UVICORN_WORKER", "1")
