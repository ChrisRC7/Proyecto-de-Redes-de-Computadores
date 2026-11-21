"""Crea la sala de alertas en Webex con el token del bot y guarda su roomId en .env.

Uso:
    python crear_sala_webex.py                          # crea la sala (si no existe) y guarda WEBEX_ROOM_ID
    python crear_sala_webex.py --miembro correo@dominio  # además agrega a esa persona a la sala
"""
import argparse
import re
from pathlib import Path

import requests

import config

API = "https://webexapis.com/v1"
TITULO = "CE5301 - Alertas de red"
ENV = Path(__file__).with_name(".env")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--miembro", nargs="*", default=[], help="Correos a agregar a la sala")
    parser.add_argument("--titulo", default=TITULO)
    args = parser.parse_args()

    if not config.WEBEX_TOKEN:
        raise SystemExit("Falta WEBEX_TOKEN en .env")
    h = {"Authorization": f"Bearer {config.WEBEX_TOKEN}"}

    yo = requests.get(f"{API}/people/me", headers=h, timeout=30)
    yo.raise_for_status()
    print(f"Bot autenticado: {yo.json().get('displayName')} ({yo.json().get('emails', ['?'])[0]})")

    salas = requests.get(f"{API}/rooms", headers=h, params={"type": "group", "max": 100}, timeout=30)
    salas.raise_for_status()
    sala = next((s for s in salas.json().get("items", []) if s["title"] == args.titulo), None)
    if sala:
        print(f"La sala '{args.titulo}' ya existe.")
    else:
        r = requests.post(f"{API}/rooms", headers=h, json={"title": args.titulo}, timeout=30)
        r.raise_for_status()
        sala = r.json()
        print(f"Sala creada: '{sala['title']}' (HTTP {r.status_code})")

    for correo in args.miembro:
        r = requests.post(f"{API}/memberships", headers=h,
                          json={"roomId": sala["id"], "personEmail": correo}, timeout=30)
        estado = "agregado" if r.ok else ("ya era miembro" if r.status_code == 409 else f"error {r.status_code}: {r.text[:200]}")
        print(f"Miembro {correo}: {estado}")

    texto = ENV.read_text(encoding="utf-8")
    texto = re.sub(r"(?m)^WEBEX_ROOM_ID=.*$", f"WEBEX_ROOM_ID={sala['id']}", texto)
    ENV.write_text(texto, encoding="utf-8")
    print("WEBEX_ROOM_ID guardado en .env")


if __name__ == "__main__":
    main()
