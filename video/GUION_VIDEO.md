# Guion del video (meta 9:00, máximo 10:00)

Cámara encendida de cada integrante durante su parte. Diapositivas en `Diapositivas.pptx`.

| Tiempo | Quién | Diapositiva | Contenido |
|---|---|---|---|
| 0:00–2:00 | Randall | 1–2 | Presentación del equipo. Problema: configurar y vigilar interfaces por CLI, equipo por equipo, es lento y propenso a errores. Qué permite el caso de uso: crear/modificar/borrar interfaces, monitorear su estado y recibir alertas en Webex. Utilidad real: menos tiempo y errores, aviso inmediato de fallas. |
| 2:00–4:00 | Javier | 3–4 | Requerimientos: sandbox Catalyst 8000v (IOS XE 17.12), VPN, Postman, Python (requests, ncclient), bot de Webex. Arquitectura (diagrama): PC, VPN, RESTCONF HTTPS 443, NETCONF SSH 830, API de Webex. Modelos YANG usados: ietf-interfaces e ietf-ip. |
| 4:00–8:30 | Christopher | 5 + demo | Seguir `caso-de-uso/demo/GUION_DEMO.md`: Postman (PUT/GET/PATCH/DELETE), script de configuración masiva, monitoreo, apagar una interfaz, alerta en Webex, NETCONF. |
| 8:30–9:00 | Randall o Javier | 6 | Cierre: 100 % de operaciones exitosas, tiempos de 0,2 a 2,3 s en promedio por tipo de operación, beneficio y mejoras futuras. |

## Antes de grabar
- [ ] Reservar de nuevo el sandbox si la reserva (vence 24 nov 13:22) ya expiró; cambiar la contraseña en `.env`.
- [ ] VPN conectada y `python demo\conectividad.py` devuelve HTTP 200.
- [ ] Ensayar una vez con cronómetro (todos).
- [ ] Verificar duración total ≤ 10:00 y que el enlace abra sin iniciar sesión.
