"""Main."""

import logging
import os
import subprocess
import tempfile

import uvicorn

from constants import (
    APP_HOST,
    APP_PORT,
    CERTBOT_EMAIL,
    CERTBOT_PROPAGATION_SECONDS,
    CERTBOT_STAGING,
    DOMAIN_NAME,
    OVH_APPLICATION_KEY,
    OVH_APPLICATION_SECRET,
    OVH_CONSUMER_KEY,
    OVH_CREDS_PATH,
    UVICORN_WORKER
)
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Write creds on disk to be processed by certbot
with open(OVH_CREDS_PATH, "w", encoding="utf-8") as f_:
    f_.write(
        f"""
dns_ovh_endpoint = ovh-eu
dns_ovh_application_key = {OVH_APPLICATION_KEY}
dns_ovh_application_secret = {OVH_APPLICATION_SECRET}
dns_ovh_consumer_key = {OVH_CONSUMER_KEY}
"""
    )
os.chmod(OVH_CREDS_PATH, 0o600)


app = FastAPI()


@app.get("/", include_in_schema=False)
def health_check():
    """Healthcheck."""
    return JSONResponse(content={"status": "OK"})


@app.get("/generate_certificate/{subdomain}")
def generate_certificate(subdomain: str):
    """
    Generate certificate
    """
    with tempfile.TemporaryDirectory() as tmpdir:

        os.symlink("/etc/letsencrypt/accounts/", f"{tmpdir}/accounts", target_is_directory=True)

        try:
            # Commande certbot pour obtenir un certificat SSL
            command_certbot = f"""certbot certonly \
            --dns-ovh \
            --dns-ovh-credentials {OVH_CREDS_PATH} \
            --non-interactive \
            --work-dir {tmpdir} \
            --logs-dir {tmpdir}/logs \
            --config-dir {tmpdir} \
            --agree-tos \
            --email {CERTBOT_EMAIL} \
            -d {subdomain}.{DOMAIN_NAME} \
            --dns-ovh-propagation-seconds {CERTBOT_PROPAGATION_SECONDS}"""

            if CERTBOT_STAGING:
                command_certbot += " --staging"

            # Lancement de la commande en utilisant subprocess
            subprocess.run(command_certbot, shell=True, check=True)

        except subprocess.CalledProcessError as exception:
            logging.error(exception)
            raise HTTPException(status_code=500, detail="Subprocess error") from exception

        except Exception as exception:
            logging.error(exception)
            raise HTTPException(status_code=500, detail="Error") from exception

        path_fullchain = f"{tmpdir}/live/{subdomain}.{DOMAIN_NAME}/fullchain.pem"
        path_privkey = f"{tmpdir}/live/{subdomain}.{DOMAIN_NAME}/privkey.pem"

        with open(path_fullchain, "r", encoding="utf-8") as file:
            fullchain = file.read()
        with open(path_privkey, "r", encoding="utf-8") as file:
            privkey = file.read()

        return {
            "message": f"Certificate for {subdomain}.{DOMAIN_NAME} generated successfully",
            "privkey": {privkey},
            "fullchain": {fullchain},
        }


if __name__ == "__main__":
    uvicorn.run(app, host=APP_HOST, port=APP_PORT, workers=int(UVICORN_WORKER))
