"""Monitoreo del estado operativo de interfaces por RESTCONF + alertas a Webex.

Consulta ietf-interfaces:interfaces-state (estado operativo, contadores) y lo cruza
con ietf-interfaces:interfaces (configuración: descripción, enabled). Si alguna
interfaz vigilada está caída (oper-status != up), envía un mensaje a una sala de
Webex usando la API de Webex (POST https://webexapis.com/v1/messages).

Uso:
    python monitorear_interfaces.py                       # todas las interfaces, una vez
    python monitorear_interfaces.py --solo Loopback501 GigabitEthernet1
    python monitorear_interfaces.py --intervalo 60        # repetir cada 60 s (Ctrl+C para salir)
    python monitorear_interfaces.py --sin-webex           # no enviar alertas
    python monitorear_interfaces.py --probar-webex        # envía un mensaje de prueba y sale
"""
import argparse
import csv
import time
from datetime import datetime
from pathlib import Path

import requests

import config

AQUI = Path(__file__).parent
WEBEX_URL = "https://webexapis.com/v1/messages"


def obtener(sesion: requests.Session, ruta: str):
    inicio = time.perf_counter()
    resp = sesion.get(f"{config.base_url()}/{ruta}", timeout=30, verify=False)
    ms = (time.perf_counter() - inicio) * 1000
    resp.raise_for_status()
    return resp.json(), ms


def consultar(sesion: requests.Session):
    estado, ms_estado = obtener(sesion, "ietf-interfaces:interfaces-state")
    conf, ms_conf = obtener(sesion, "ietf-interfaces:interfaces")
    confs = {i["name"]: i for i in conf.get("ietf-interfaces:interfaces", {}).get("interface", [])}

    filas = []
    for itf in estado.get("ietf-interfaces:interfaces-state", {}).get("interface", []):
        c = confs.get(itf["name"], {})
        stats = itf.get("statistics", {})
        filas.append({
            "nombre": itf["name"],
            "descripcion": c.get("description", ""),
            "admin": itf.get("admin-status", "?"),
            "oper": itf.get("oper-status", "?"),
            "velocidad": itf.get("speed", ""),
            "in_octets": stats.get("in-octets", ""),
            "out_octets": stats.get("out-octets", ""),
        })
    return filas, ms_estado, ms_conf


def enviar_webex(texto: str) -> int:
    if not config.WEBEX_TOKEN or not config.WEBEX_ROOM_ID:
        print("  (Webex no configurado: faltan WEBEX_TOKEN / WEBEX_ROOM_ID en .env)")
        return 0
    inicio = time.perf_counter()
    resp = requests.post(
        WEBEX_URL,
        headers={"Authorization": f"Bearer {config.WEBEX_TOKEN}"},
        json={"roomId": config.WEBEX_ROOM_ID, "markdown": texto},
        timeout=30,
    )
    ms = (time.perf_counter() - inicio) * 1000
    print(f"  Webex: HTTP {resp.status_code} en {ms:.1f} ms")
    if resp.status_code >= 300:
        print("  " + resp.text[:300])
    return resp.status_code


def ciclo(sesion, args) -> None:
    filas, ms_estado, ms_conf = consultar(sesion)
    if args.solo:
        filas = [f for f in filas if f["nombre"] in args.solo]

    ahora = datetime.now()
    print(f"\n[{ahora:%Y-%m-%d %H:%M:%S}] {config.HOST}  "
          f"(interfaces-state {ms_estado:.0f} ms, interfaces {ms_conf:.0f} ms)")
    print(f"  {'Interfaz':<24}{'Admin':<8}{'Oper':<18}Descripción")
    caidas = []
    for f in filas:
        marca = "" if f["oper"] == "up" else "  <-- CAÍDA"
        print(f"  {f['nombre']:<24}{f['admin']:<8}{f['oper']:<18}{f['descripcion']}{marca}")
        if f["oper"] != "up":
            caidas.append(f)

    print(f"  Total: {len(filas)} interfaces, {len(filas) - len(caidas)} up, {len(caidas)} caídas")

    if caidas and not args.sin_webex:
        lineas = [f"🚨 **Alerta de red** — {config.HOST}",
                  f"{len(caidas)} interfaz(es) caída(s) a las {ahora:%H:%M:%S}:"]
        for f in caidas:
            lineas.append(f"- **{f['nombre']}** — admin: {f['admin']}, oper: {f['oper']}"
                          + (f" ({f['descripcion']})" if f["descripcion"] else ""))
        enviar_webex("\n".join(lineas))

    salida = AQUI / "resultados"
    salida.mkdir(exist_ok=True)
    archivo = salida / "monitoreo.csv"
    nuevo = not archivo.exists()
    with archivo.open("a", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        if nuevo:
            w.writerow(["fecha", "interfaz", "admin", "oper", "tiempo_estado_ms", "tiempo_config_ms"])
        for f in filas:
            w.writerow([ahora.isoformat(timespec="seconds"), f["nombre"], f["admin"], f["oper"],
                        round(ms_estado, 1), round(ms_conf, 1)])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--solo", nargs="*", help="Nombres de interfaces a vigilar")
    parser.add_argument("--intervalo", type=int, default=0, help="Segundos entre consultas (0 = una sola vez)")
    parser.add_argument("--sin-webex", action="store_true")
    parser.add_argument("--probar-webex", action="store_true")
    args = parser.parse_args()

    if args.probar_webex:
        enviar_webex("✅ Prueba del bot de monitoreo RESTCONF (CE-5301).")
        return

    config.require_credentials()
    sesion = requests.Session()
    sesion.auth = (config.USER, config.PASSWORD)
    sesion.headers.update(config.HEADERS)

    try:
        while True:
            ciclo(sesion, args)
            if args.intervalo <= 0:
                break
            time.sleep(args.intervalo)
    except KeyboardInterrupt:
        print("\nMonitoreo detenido.")


if __name__ == "__main__":
    main()
