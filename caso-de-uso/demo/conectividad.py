"""Prueba de conectividad RESTCONF: GET de la configuración de interfaces (ietf-interfaces)."""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import requests  # noqa: E402

import config  # noqa: E402

config.require_credentials()
url = f"{config.base_url()}/ietf-interfaces:interfaces"
inicio = time.perf_counter()
resp = requests.get(url, auth=(config.USER, config.PASSWORD), headers=config.HEADERS, verify=False, timeout=30)
ms = (time.perf_counter() - inicio) * 1000
print(f"GET {url}")
print(f"HTTP {resp.status_code}  {ms:.0f} ms  ({resp.headers.get('Content-Type', '')})")
if resp.ok:
    for itf in resp.json()["ietf-interfaces:interfaces"]["interface"]:
        print(f"  {itf['name']:<20} enabled={str(itf.get('enabled')):<6} {itf.get('description', '')}")
