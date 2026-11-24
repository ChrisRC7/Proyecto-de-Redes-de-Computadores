# TODO — Desafío de Redes (CE-5301)

Detalle de cada requisito y rúbricas en [REQUERIMIENTOS.md](REQUERIMIENTOS.md).

**Entrega:** jueves 26 de noviembre de 2026.
**Integrantes:** Christopher · Randall · Javier

> **Caso de uso aprobado por el profesor (18 nov).** Pidió al menos tres funcionalidades; la tercera (alertas a Webex) también fue aprobada. Registrar esta respuesta en la Minuta 1.

---

## Caso de uso aprobado

**Funcionalidades (3):**
1. **Configuración:** crear, modificar y borrar interfaces (Postman PUT/PATCH/DELETE + script Python de configuración masiva).
2. **Monitoreo:** consultar el estado operativo de las interfaces (Postman GET + script Python de monitoreo).
3. **Alertas a Webex:** enviar un mensaje a una sala de Webex cuando una interfaz esté caída.


**Configuración y monitoreo de interfaces de un router Cisco IOS XE mediante RESTCONF**, usando el sandbox gratuito "IOS XE on Cat8kv Always-On" de developer.cisco.com.

- **Postman:** colección con GET/PUT/PATCH/DELETE sobre el modelo YANG `ietf-interfaces` (crear una loopback, cambiar descripción, consultar estado, borrarla).
- **Python (`requests`):** script que aplica la misma configuración a una lista de interfaces/dispositivos y otro que consulta el estado operativo y avisa si una interfaz está caída.
- **Utilidad real:** reemplaza entrar por CLI equipo por equipo; cubre las áreas de *configuración* y *monitoreo* del enunciado.

- **Webex (obligatorio):** el script de monitoreo envía la alerta a un espacio de Webex mediante su API (integración de APIs).

---

## Roles

| Persona | Rol | Responsabilidad principal |
|---|---|---|
| **Christopher** | Coordinador + líder técnico | Caso de uso (Postman/Python), sandbox, Anexo 1, investigación bloque C (NETCONF), convoca reuniones |
| **Randall** | Líder de investigación + editor del informe | Investigación bloques A y B, integración y formato del informe, referencias APA |
| **Javier** | Líder de documentación de equipo + video | Investigación bloque D (RESTCONF y herramientas), Anexo 2 (minutas, cronograma), guion y edición del video |

Carga equilibrada: cada persona investiga, escribe una parte del informe, lleva su bitácora y presenta en el video.

---

## Fase 0 — Arranque (12 nov a 14 nov)

**Todos**
- [x] **Reunión 1 (kickoff):** confirmar caso de uso, roles, reglas del equipo y cronograma → **Minuta 1** — *Minuta 1 redactada en el Anexo 2; falta la captura real de esa reunión*
- [ ] Crear carpeta compartida (Drive/OneDrive) y repositorio para el código
- [ ] Cada quien abre su **bitácora** personal desde hoy (fecha, actividad, duración)

**Christopher**
- [x] Crear cuenta en developer.cisco.com y reservar/probar el sandbox — *los Always On (Cat8000v y Cat9000v) están caídos del lado de Cisco (reportado en Cisco Community 19–22 nov). Se usa el **Catalyst 8000v on-demand** (privado, IOS XE 17.12.02), reservado 22 nov 13:22 → **24 nov 13:22**; acceso por VPN con OpenConnect GUI 1.6.2 (`D:\Programacion\Herramientas\OpenConnect-GUI`, perfil con Interface name `devnet`); router `10.10.20.48`. Reservar de nuevo antes de grabar el video si la reserva ya venció*
- [x] Instalar Postman y Python (`requests`, `ncclient`, `pyang`) — *Python y librerías listos; la colección se corre con Newman (`D:\Programacion\Herramientas
ewman`)*

**Randall**
- [x] Crear la plantilla del informe con el formato exigido (Arial 12, justificado, títulos Arial 12 negrita, pies de tabla/figura Arial 11)

**Javier**
- [ ] Crear plantillas de minuta y de bitácora
- [ ] Redactar borrador de metas, roles, reglas y cronograma para el Anexo 2

---

## Fase 1 — Investigación (14 nov a 18 nov)

Cada dato con su cita; nada de Wikipedia.

**Randall — Bloque A: Programabilidad basada en modelos**
- [ ] ¿Qué hace un equipo de DevOps?
- [ ] Rol de SNMP
- [ ] ¿Qué es el RFC 3535?
- [ ] Definición de Model Driven Programmability
- [ ] Bloques básicos de construcción
- [ ] ¿Qué es un modelo de datos?

**Randall — Bloque B: YANG**
- [ ] ¿Qué es YANG?
- [ ] Lenguaje YANG vs. modelos de datos YANG vs. YANG data
- [ ] Estructura del modelo de datos YANG y cómo se usa
- [ ] pyang: qué es y cómo se usa (con captura de `pyang -f tree`) — *salida lista en `caso-de-uso/yang/` (ietf-interfaces rev. 2018-02-20 + ietf-ip, pyang 2.7.1)*

**Christopher — Bloque C: NETCONF**
- [x] ¿Qué es NETCONF y bajo qué estándar fue creado?
- [x] Cómo funcionan las comunicaciones y por qué se crearon
- [x] Protocolo de transporte por defecto
- [x] Ejemplo de llamada NETCONF a un equipo (comando + caso de uso), probado en el sandbox — *`netconf_ejemplo.py --capacidades` OK 22 nov: sesión en 2,8 s, `<get-config>` en 389 ms; salida en `caso-de-uso/resultados/netconf_get_config.txt`*
- [x] Qué es una RPC y formato de los mensajes

**Javier — Bloque D: RESTCONF y herramientas**
- [ ] ¿Qué es RESTCONF, diferencia con NETCONF y mayor ventaja?
- [ ] Relación entre modelos YANG y llamadas API RESTCONF
- [ ] Qué es Postman, requerimientos y uso para llamadas API
- [ ] Llamadas RESTCONF con Postman y con Python (apoyarse en lo que arme Christopher)
- [ ] Tres herramientas de automatización (p. ej. Ansible, Puppet, Chef/SaltStack): push o pull, diseño del sistema central, sistemas operativos

**Todos**
- [x] **Reunión 2 (avance de investigación + demo preliminar)** → **Minuta 2** — *Minuta 2 redactada; falta la captura real*

---

## Fase 2 — Caso de uso (15 nov a 20 nov)

**Christopher**
- [x] Verificar conectividad RESTCONF al sandbox (GET a `/restconf/data/ietf-interfaces:interfaces`) — *HTTP 200 en ~0,7 s por la VPN (22 nov)*
- [x] Colección Postman: variables de entorno, GET, PUT/POST, PATCH, DELETE — *ejecutada 23 nov con Newman: 10 peticiones, 20 aserciones, 0 fallos; `caso-de-uso/resultados/postman/`*
- [x] Script Python de configuración (varias interfaces o dispositivos) — *probado 22 nov: crear (PUT 201), listar (GET 200), modificar (PATCH 204), apagar/encender (PATCH 204), borrar (DELETE 204), 100 % éxito*
- [x] Script Python de monitoreo de interfaces — *probado 22 nov: detectó Loopback502 apagada y envió la alerta a Webex (HTTP 200)*
- [x] Crear bot y token en developer.webex.com y una sala para las alertas — *bot "CE5301 Alertas RESTCONF", sala "CE5301 - Alertas de red"*
- [x] Integrar el envío de alerta a Webex en el script de monitoreo (cuando una interfaz esté caída) — *mensaje de prueba recibido (HTTP 200)*
- [x] Guardar capturas de cada request/response (inputs y outputs) y tiempos de respuesta para la validación cuantitativa — *listo 22 nov: 11 capturas de terminal (`caso-de-uso/capturas/terminal/`), alerta en Webex, VPN y reserva; CSV y logs en `caso-de-uso/resultados/`. Postman: `caso-de-uso/capturas/postman/`*
- [x] Preparar la demo del video — *`caso-de-uso/demo/demo_caso_de_uso.ps1` (pasos con pausa), guion con tiempos en `caso-de-uso/demo/GUION_DEMO.md` y grabación de respaldo sin audio `caso-de-uso/capturas/video/demo_terminal_sin_audio.mp4` (2:45) con su guion de lectura sincronizado `GUION_LECTURA.md`. La parte con cámara y voz la graba Christopher*
- [x] Subir código al repositorio con README — *push de `ChrisDevelopment` a GitHub (22 nov); falta merge a `main`*

**Randall**
- [ ] Probar la colección y los scripts en su máquina siguiendo el README (validación independiente)
- [ ] Tomar capturas del `show running-config` / verificación antes y después
- [ ] Verificar que la alerta llegue a la sala de Webex (captura del mensaje)

**Javier**
- [ ] Documentar el problema, la solución y las herramientas mientras Christopher lo implementa
- [x] Hacer el diagrama de la arquitectura (PC ↔ Internet ↔ sandbox, flujo de la llamada REST)

---

## Fase 3 — Informe (18 nov a 23 nov)

| Sección | Redacta | Revisa |
|---|---|---|
| Portada e Índice | Randall | Javier |
| Objetivos del Desafío | Randall | Christopher |
| Investigación | Christopher, Randall, Javier (su bloque) | Randall integra |
| Caso de Uso | Christopher + Javier | Randall |
| Resultados y Análisis | Christopher | Javier |
| Conclusiones y Recomendaciones | Todos (1 párrafo cada uno) | Randall integra |
| Referencias (APA) | Randall | Christopher |
| Anexo 1: Código/Configuraciones | Christopher | Randall |
| Anexo 2: Trabajo Individual y en Equipo | Javier | Christopher |

**Christopher**
- [x] Redactar Caso de Uso (parte técnica) y Resultados con capturas y datos cuantitativos
- [x] Armar Anexo 1 (scripts, colección exportada, enlace al repositorio)

**Randall**
- [ ] Integrar todos los bloques de investigación con estilo uniforme
- [ ] Unificar referencias en APA y verificar que **cada dato teórico tenga cita**
- [x] Numerar tablas y figuras con el formato "**Tabla #1.** Descripción"
- [ ] Revisar **página por página** que todo esté justificado
- [x] Generar índice automático

**Javier**
- [ ] Anexo 2: metas, roles, reglas, cronograma con responsables y fechas
- [ ] Anexo 2: las 3+ minutas y las 3 bitácoras individuales
- [ ] Anexo 2: reflexión grupal sobre eficiencia, equidad y colaboración (TE5–TE7)

---

## Fase 4 — Video (21 nov a 24 nov)

**Javier**
- [x] Guion con tiempos (meta: 9 min, para tener margen)
- [x] Diapositivas breves de apoyo
- [ ] Editar y unir las partes; verificar duración **≤ 10:00**
- [ ] Subir (YouTube no listado o Drive) y comprobar que el enlace abre sin iniciar sesión

**Reparto sugerido (cada quien con cámara encendida)**

| Tiempo | Quién | Contenido |
|---|---|---|
| 0:00–2:00 | Randall | Introducción: qué permite hacer el caso de uso y su utilidad real |
| 2:00–4:00 | Javier | Requerimientos mínimos de red, aplicaciones usadas y arquitectura |
| 4:00–8:30 | Christopher | Configuración, scripts y demostración en vivo (Postman + Python) |
| 8:30–9:00 | Randall o Javier | Cierre: resultados y beneficio |

**Todos**
- [ ] Ensayar una vez con cronómetro
- [ ] Grabar cada parte con cámara
- [x] **Reunión 3 (revisión del video e informe)** → **Minuta 3** — *Minuta 3 con captura real del 23 nov*

---

## Fase 5 — Cierre y entrega (24 nov a 26 nov)

**Randall**
- [ ] Insertar el enlace del video en la sección Caso de Uso
- [ ] Revisión final de ortografía y formato; exportar a **PDF**

**Christopher**
- [ ] Revisión cruzada del PDF contra la tabla de puntaje de [REQUERIMIENTOS.md](REQUERIMIENTOS.md)
- [ ] Subir **una sola copia** a TEC Digital, ítem "Presentación Final: Desafío Redes"

**Javier**
- [ ] Verificar que el Anexo 2 tenga 3+ minutas y 3 bitácoras completas
- [ ] Confirmar que el enlace del video funciona desde otra cuenta

**Todos (individual, obligatorio)**
- [ ] Christopher llenó el formulario de evaluación individual y coevaluación
- [ ] Randall llenó el formulario
- [ ] Javier llenó el formulario

---

## Reuniones mínimas (se exigen al menos 3 con minuta)

| # | Cuándo | Tema | Minuta |
|---|---|---|---|
| 1 | 12 nov | Kickoff: caso de uso, roles, reglas, cronograma | Javier |
| 2 | 18 nov | Avance de investigación y demo preliminar | Randall |
| 3 | 23 nov | Revisión de informe y video | Christopher |
| 4 (opcional) | 25 nov | Cierre y lecciones aprendidas | Javier |

Cada minuta: fecha, hora, medio, asistentes, agenda, acuerdos, tareas con responsable y fecha, y una captura de la reunión como evidencia.
