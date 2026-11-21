"""Ejemplo de llamada NETCONF (bloque C de la investigación) con ncclient.

Abre una sesión NETCONF sobre SSH (puerto 830), muestra las capacidades anunciadas
en el <hello> y ejecuta la RPC <get-config> con un filtro subtree sobre el modelo
ietf-interfaces. Imprime el XML de la respuesta (<rpc-reply>).

Uso:
    python netconf_ejemplo.py                # get-config de interfaces
    python netconf_ejemplo.py --capacidades  # además lista las capacidades YANG
"""
import argparse
import time

from ncclient import manager

import config

FILTRO = """
<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces"/>
</filter>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--capacidades", action="store_true")
    args = parser.parse_args()
    config.require_credentials()

    inicio = time.perf_counter()
    with manager.connect(
        host=config.HOST, port=830, username=config.USER, password=config.PASSWORD,
        hostkey_verify=False, look_for_keys=False, allow_agent=False, timeout=60,
    ) as m:
        print(f"Sesión NETCONF abierta (id {m.session_id}) en {(time.perf_counter() - inicio) * 1000:.0f} ms")
        if args.capacidades:
            for cap in m.server_capabilities:
                print("  ", cap)
        inicio = time.perf_counter()
        reply = m.get_config(source="running", filter=FILTRO)
        print(f"<get-config> respondió en {(time.perf_counter() - inicio) * 1000:.0f} ms\n")
        print(reply.xml)


if __name__ == "__main__":
    main()
