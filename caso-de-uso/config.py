"""Configuración compartida: lee credenciales desde variables de entorno o un archivo .env.

Nunca se suben credenciales al repositorio: copie `.env.example` a `.env` y complételo.
"""
import os
from pathlib import Path

import urllib3

# El sandbox usa un certificado autofirmado.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def _load_env_file() -> None:
    env_path = Path(__file__).with_name(".env")
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_env_file()

HOST = os.getenv("RESTCONF_HOST", "10.10.20.48")
PORT = int(os.getenv("RESTCONF_PORT", "443"))
USER = os.getenv("RESTCONF_USER", "")
PASSWORD = os.getenv("RESTCONF_PASSWORD", "")

WEBEX_TOKEN = os.getenv("WEBEX_TOKEN", "")
WEBEX_ROOM_ID = os.getenv("WEBEX_ROOM_ID", "")

HEADERS = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json",
}


def base_url(host: str = HOST, port: int = PORT) -> str:
    return f"https://{host}:{port}/restconf/data"


def require_credentials() -> None:
    if not USER or not PASSWORD:
        raise SystemExit("Faltan RESTCONF_USER / RESTCONF_PASSWORD (ver .env.example).")
