"""Configuración masiva de interfaces por RESTCONF (modelo YANG ietf-interfaces).

Lee una lista de dispositivos e interfaces desde interfaces.json y aplica la misma
operación a todas, en lugar de entrar por CLI equipo por equipo.

Uso:
    python configurar_interfaces.py crear       # PUT: crea/reemplaza cada loopback
    python configurar_interfaces.py modificar --descripcion "Nuevo texto"   # PATCH
    python configurar_interfaces.py apagar --solo Loopback501   # PATCH enabled=false (shutdown)
    python configurar_interfaces.py encender --solo Loopback501 # PATCH enabled=true
    python configurar_interfaces.py borrar      # DELETE
    python configurar_interfaces.py listar      # GET de la configuración actual

Cada operación imprime el código HTTP y el tiempo de respuesta, y guarda un CSV en
resultados/ para la validación cuantitativa del informe.
"""
import argparse
import csv
import json
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

import requests

import config

AQUI = Path(__file__).parent


def url_interfaz(host: str, port: int, nombre: str) -> str:
    return f"{config.base_url(host, port)}/ietf-interfaces:interfaces/interface={quote(nombre, safe='')}"


def cuerpo_interfaz(itf: dict, descripcion: str | None = None) -> dict:
    return {
        "ietf-interfaces:interface": {
            "name": itf["nombre"],
            "description": descripcion or itf["descripcion"],
            "type": "iana-if-type:softwareLoopback",
            "enabled": True,
            "ietf-ip:ipv4": {
                "address": [{"ip": itf["ip"], "netmask": itf["mascara"]}]
            },
        }
    }


def ejecutar(sesion: requests.Session, metodo: str, url: str, cuerpo: dict | None = None):
    inicio = time.perf_counter()
    resp = sesion.request(metodo, url, json=cuerpo, timeout=30, verify=False)
    ms = (time.perf_counter() - inicio) * 1000
    return resp, ms


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("accion", choices=["crear", "modificar", "apagar", "encender", "borrar", "listar"])
    parser.add_argument("--solo", nargs="*", help="Aplicar solo a estas interfaces")
    parser.add_argument("--descripcion", help="Nueva descripción (para 'modificar')")
    parser.add_argument("--archivo", default=str(AQUI / "interfaces.json"))
    args = parser.parse_args()

    config.require_credentials()
    inventario = json.loads(Path(args.archivo).read_text(encoding="utf-8"))

    sesion = requests.Session()
    sesion.auth = (config.USER, config.PASSWORD)
    sesion.headers.update(config.HEADERS)

    filas = []
    for disp in inventario["dispositivos"]:
        host, port = disp.get("host", config.HOST), disp.get("port", config.PORT)
        print(f"\n== {disp['nombre']} ({host}) ==")
        for itf in disp["interfaces"]:
            if args.solo and itf["nombre"] not in args.solo:
                continue
            url = url_interfaz(host, port, itf["nombre"])
            if args.accion == "crear":
                resp, ms = ejecutar(sesion, "PUT", url, cuerpo_interfaz(itf))
            elif args.accion == "modificar":
                cuerpo = {"ietf-interfaces:interface": {
                    "name": itf["nombre"],
                    "description": args.descripcion or itf["descripcion"] + " (modificada)",
                }}
                resp, ms = ejecutar(sesion, "PATCH", url, cuerpo)
            elif args.accion in ("apagar", "encender"):
                cuerpo = {"ietf-interfaces:interface": {
                    "name": itf["nombre"], "enabled": args.accion == "encender"}}
                resp, ms = ejecutar(sesion, "PATCH", url, cuerpo)
            elif args.accion == "borrar":
                resp, ms = ejecutar(sesion, "DELETE", url)
            else:
                resp, ms = ejecutar(sesion, "GET", url)

            ok = resp.status_code in (200, 201, 204)
            estado = "OK " if ok else "ERR"
            print(f"  [{estado}] {args.accion:<9} {itf['nombre']:<12} HTTP {resp.status_code}  {ms:7.1f} ms")
            if args.accion == "listar" and ok:
                print("        " + json.dumps(resp.json(), ensure_ascii=False))
            elif not ok and resp.text:
                print("        " + resp.text.strip().replace("\n", " ")[:300])
            filas.append({
                "fecha": datetime.now().isoformat(timespec="seconds"),
                "dispositivo": disp["nombre"],
                "interfaz": itf["nombre"],
                "accion": args.accion,
                "http": resp.status_code,
                "tiempo_ms": round(ms, 1),
            })

    exitos = sum(1 for f in filas if f["http"] in (200, 201, 204))
    promedio = sum(f["tiempo_ms"] for f in filas) / len(filas) if filas else 0
    print(f"\nResumen: {exitos}/{len(filas)} operaciones exitosas, tiempo promedio {promedio:.1f} ms")

    salida = AQUI / "resultados"
    salida.mkdir(exist_ok=True)
    archivo = salida / f"configuracion_{args.accion}_{datetime.now():%Y%m%d_%H%M%S}.csv"
    with archivo.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0].keys()))
        w.writeheader()
        w.writerows(filas)
    print(f"Resultados guardados en {archivo.relative_to(AQUI)}")


if __name__ == "__main__":
    main()
