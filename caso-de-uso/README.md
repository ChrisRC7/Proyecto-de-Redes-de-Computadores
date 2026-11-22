# Caso de uso: configuración y monitoreo de interfaces IOS XE con RESTCONF

Desafío de Redes (CE-5301). Automatiza tres tareas sobre un router Cisco Catalyst 8000v
(IOS XE 17.12.02) del sandbox privado **Catalyst 8000v (on-demand)** de Cisco DevNet, accedido por VPN:

1. **Configuración:** crear, modificar, apagar/encender y borrar interfaces (Postman + `configurar_interfaces.py`).
2. **Monitoreo:** consultar el estado operativo de las interfaces (Postman + `monitorear_interfaces.py`).
3. **Alertas a Webex:** cuando una interfaz está caída, el monitoreo publica un mensaje en una sala de Webex.

Todas las llamadas usan el modelo YANG estándar `ietf-interfaces` (RFC 8343) y `ietf-ip` (RFC 8344).

## Arquitectura

```
PC (Postman / Python requests)
   │
   ├──VPN AnyConnect (OpenConnect)──► devnetsandbox-usw1-reservation.cisco.com:<puerto>
   │        └── túnel 10.10.20.0/24 ──HTTPS 443 (RESTCONF, JSON) / SSH 830 (NETCONF)──► 10.10.20.48 (Cat8000v)
   │
   └──HTTPS 443 (REST, Bearer token)──► webexapis.com/v1/messages ──► Sala de Webex
```

> **Por qué on-demand y no Always On (22 nov 2026):** los sandboxes compartidos *Catalyst 8000v/9000v Always On*
> estaban caídos del lado de Cisco (sin respuesta en 443/830/22 o RESTCONF 502), reportado por otros usuarios
> en Cisco Community. Cisco recomienda la versión on-demand para trabajos que no sean pruebas rápidas.

## Requisitos

- Python 3.10+ y `pip install -r requirements.txt`
- Postman (app de escritorio o web con agente)
- Cuenta en developer.cisco.com con una reserva activa del sandbox **Catalyst 8000v** (on-demand, hasta 2 días;
  tarda ~15 min en aprovisionar). En Stack Automation → *Access Details* aparecen `vpn_address`, `vpn_username`,
  `vpn_password` y las credenciales del router (`developer` en `10.10.20.48`, puertos 22/830/443)
- Cliente VPN compatible con AnyConnect: Cisco Secure Client u **OpenConnect GUI 1.6.2**
  (infradead.org/openconnect-gui). En OpenConnect, poner en el perfil un **Interface name** corto (p. ej. `devnet`);
  con el nombre automático Windows falla con `Set up tun device failed`
- Bot de Webex (developer.webex.com → *My Webex Apps* → *Create a Bot*) agregado a una sala

## Configuración

```powershell
cd caso-de-uso
pip install -r requirements.txt
copy .env.example .env   # y completar usuario, contraseña, token y roomId
```

Bot del proyecto: **CE5301 Alertas RESTCONF** (`ce5301-restconf-alertas@webex.bot`).
Con `WEBEX_TOKEN` en `.env`, el script crea la sala "CE5301 - Alertas de red", guarda su `WEBEX_ROOM_ID`
y agrega a los integrantes:

```powershell
python crear_sala_webex.py --miembro correo1@ejemplo.com correo2@ejemplo.com
python monitorear_interfaces.py --probar-webex
```

## Uso — Python

```powershell
python configurar_interfaces.py crear                       # PUT Loopback501-503 (interfaces.json)
python configurar_interfaces.py listar                      # GET de cada una
python configurar_interfaces.py modificar --descripcion "Enlace de pruebas"   # PATCH
python monitorear_interfaces.py --solo Loopback501 Loopback502 Loopback503
python configurar_interfaces.py apagar --solo Loopback502   # shutdown
python monitorear_interfaces.py --solo Loopback501 Loopback502 Loopback503     # detecta la caída y alerta a Webex
python configurar_interfaces.py borrar                      # DELETE (limpieza)
python monitorear_interfaces.py --probar-webex              # solo prueba el bot
python monitorear_interfaces.py --intervalo 60              # monitoreo continuo
python netconf_ejemplo.py --capacidades                     # ejemplo NETCONF (get-config) para la investigación
```

Cada ejecución imprime código HTTP y tiempo de respuesta, y guarda CSV en `resultados/` para la sección de
Resultados del informe.

Para agregar más equipos o interfaces basta con editar `interfaces.json`.

## Uso — Postman

1. *Import* → `postman/CE5301-RESTCONF.postman_collection.json` y `postman/CE5301-Cat8kv.postman_environment.json`.
2. Seleccionar el entorno *CE5301 - Cat8kv Sandbox* y completar `username`, `password`, `webex_token`, `webex_room_id`.
3. *Settings* → desactivar *SSL certificate verification* (certificado autofirmado).
4. Ejecutar las peticiones 1 → 10 en orden (o *Run collection*). Cada petición valida 2xx y tiempo < 5 s.

| # | Método | Recurso | Respuesta esperada |
|---|---|---|---|
| 1 | GET | `/restconf` | 200 |
| 2 | GET | `/restconf/data/ietf-interfaces:interfaces` | 200 |
| 3 | PUT | `.../interfaces/interface=Loopback500` | 201 / 204 |
| 4 | GET | `.../interfaces/interface=Loopback500` | 200 |
| 5 | PATCH | `.../interfaces/interface=Loopback500` (description) | 204 |
| 6 | GET | `.../interfaces-state/interface=Loopback500` | 200 (oper-status up) |
| 7 | PATCH | `.../interfaces/interface=Loopback500` (enabled=false) | 204 |
| 8 | GET | `/restconf/data/ietf-interfaces:interfaces-state` | 200 |
| 9 | DELETE | `.../interfaces/interface=Loopback500` | 204 |
| 10 | POST | `https://webexapis.com/v1/messages` | 200 |

## Notas

- El sandbox es **compartido**: usar solo loopbacks propias (500–503) y no tocar GigabitEthernet1
  (gestión) para no cortar la conectividad.
- `.env` está en `.gitignore`; nunca subir credenciales ni el token del bot.
