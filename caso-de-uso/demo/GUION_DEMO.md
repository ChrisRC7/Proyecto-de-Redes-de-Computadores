# Guion de la demo — video (Christopher, 4:00 a 8:30)

Duración objetivo: **4 min 30 s**. Cámara encendida en una esquina (OBS: fuente "Captura de pantalla" + "Dispositivo de video").

## Antes de grabar (checklist)

- [ ] Reserva activa del sandbox **Catalyst 8000v** (on-demand) en developer.cisco.com → *Reservations*.
- [ ] VPN conectada en OpenConnect (candado **verde**, perfil con Interface name `devnet`).
- [ ] `caso-de-uso\.env` con la contraseña del router de **esta** reserva (cambia en cada reserva).
- [ ] Prueba rápida: `python demo\conectividad.py` → `HTTP 200`.
- [ ] Webex web abierto en la sala **CE5301 - Alertas de red**.
- [ ] Terminal grande (letra 16+), en la carpeta `caso-de-uso`.

Comando de la demo (pausa con Enter entre pasos):

```powershell
.\demo\demo_caso_de_uso.ps1
```

Respaldo: `capturas\video\demo_terminal_sin_audio.mp4` (2 min 45 s, sin audio) muestra la misma demo por si
algo falla en vivo; se puede narrar encima.

## Secuencia

| Tiempo | Pantalla | Qué decir (idea, no leer) |
|---|---|---|
| 4:00 | Stack Automation (reserva activa) → OpenConnect verde | "Usamos el sandbox Catalyst 8000v de Cisco DevNet, IOS XE 17.12. Es un router real virtualizado al que entramos por VPN. Los Always On estaban caídos esa semana, así que reservamos el privado." |
| 4:25 | Diagrama de arquitectura (Javier) | "Desde la PC, Postman y Python hablan RESTCONF por HTTPS 443 con el router; el monitoreo además llama a la API de Webex." |
| 4:45 | Paso 1 — conectividad | "Un GET a `ietf-interfaces` devuelve en JSON todas las interfaces, en menos de un segundo." |
| 5:05 | Paso 11 — árbol YANG (opcional aquí) | "Este es el modelo YANG estándar: la URL de RESTCONF sigue exactamente esta jerarquía: `interfaces/interface=nombre`." |
| 5:25 | Postman: PUT/GET/PATCH/DELETE (colección importada) | "Con Postman hacemos lo mismo a mano: crear una loopback con PUT, consultarla, cambiar la descripción con PATCH y borrarla." |
| 6:10 | Paso 2 — crear (PUT 201 ×3) | "Ahora con Python: el script lee una lista en `interfaces.json` y crea tres loopbacks de una vez. Esto reemplaza entrar por CLI equipo por equipo." |
| 6:30 | Paso 3–4 — listar y modificar (200 / 204) | "Verificamos y cambiamos la descripción a las tres con PATCH; cada operación registra el código HTTP y el tiempo." |
| 6:55 | Paso 5 — monitoreo (3 up) | "El script de monitoreo lee `interfaces-state`: estado administrativo y operativo." |
| 7:10 | Paso 6 — apagar Loopback502 | "Simulamos una falla apagando una interfaz." |
| 7:20 | Paso 7 — alerta → **cambiar a Webex** | "El monitoreo la detecta como caída y envía una alerta a la sala de Webex por su API REST… y aquí llega el mensaje." |
| 7:50 | Paso 8–9 — encender y borrar | "La recuperamos y limpiamos: el router queda como estaba." |
| 8:05 | Paso 10 — NETCONF | "Por último, la misma información por NETCONF: sesión SSH en el puerto 830 y la RPC `get-config`, que responde en XML." |
| 8:20 | Tabla de tiempos (Resultados) | "En total, 100 % de operaciones exitosas, con tiempos entre 0,15 y 2,7 segundos." → pasa a Randall/Javier. |

## Capturas para el informe (`caso-de-uso/capturas/`)

| Archivo | Uso en el informe |
|---|---|
| `sandbox_cat8kv_ondemand_reserva.jpg` | Caso de uso → requerimientos (sandbox y acceso) |
| `vpn_openconnect_conectada.jpg` | Caso de uso → requerimientos de red (VPN) |
| `terminal/01_conectividad.png` | Validación de conectividad RESTCONF |
| `terminal/02_crear.png` … `09_borrar.png` | Resultados: cada operación con código HTTP y tiempo |
| `terminal/07_alerta.png` + `webex_alerta_interfaz_caida.jpg` | Resultados: detección de falla y alerta |
| `terminal/10_netconf.png` | Investigación bloque C (ejemplo NETCONF) |
| `terminal/11_yang.png` | Investigación bloque B (pyang -f tree) |

Los tiempos exactos están en `caso-de-uso/resultados/*.csv` y en el log `ejecucion_*.log`.
