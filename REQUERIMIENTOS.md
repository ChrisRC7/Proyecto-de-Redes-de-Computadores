# Requerimientos — Trabajo Final: Desafío de Redes

**Curso:** CE-5301 Redes de Computadoras · II Semestre 2026 · Prof. Rodolfo Tacsan Chaves
**Fuente:** `desafio-redes_DESAFÍO_REDES.pdf` (los números entre paréntesis son las secciones del enunciado).
**Peso:** los proyectos valen 30 % de la nota del curso (programa del curso, sección 6).

**Fecha de entrega:** jueves 26 de noviembre de 2026.

---

## 1. Resumen: qué hay que entregar

| # | Entregable | Dónde / cómo | Peso |
|---|---|---|---|
| 1 | **Informe final en PDF** (una sola copia por grupo) | TEC Digital, ítem "Presentación Final: Desafío Redes" | 50 % |
| 2 | **Video del caso de uso** (≤ 10 min) | Enlace dentro del informe (sección Caso de Uso) | 50 % |
| 3 | **Formulario de evaluación individual + coevaluación** | Google Forms, lo llena **cada estudiante**, una sola vez | Parte de la nota TE |

Formulario: <https://docs.google.com/forms/d/e/1FAIpQLSfC_crNLh92D2pbcmpS1f_geWVgdBkoXvHkjbXpWi53Q9b6UQ/viewform>

El proyecto se hace en los mismos grupos usados durante el semestre (6.1).

---

## 2. Parte 1 — Investigación (3.1)

Temas **mínimos** que debe cubrir el informe. Cada dato teórico necesita su cita (ver sección 6).

### 2.1 ¿Qué es y por qué la programabilidad basada en modelos?
- [ ] ¿Qué hace un equipo de DevOps?
- [ ] Rol de SNMP
- [ ] ¿Qué es el RFC 3535?
- [ ] Definición de Programación basada en Modelos (Model Driven Programmability) en redes
- [ ] Bloques básicos de construcción de la programabilidad basada en modelos
- [ ] ¿Qué es un modelo de datos?

### 2.2 Introducción a YANG
- [ ] ¿Qué es YANG?
- [ ] Diferencia entre lenguaje YANG, modelos de datos YANG y YANG data
- [ ] Estructura del modelo de datos YANG y cómo se usa
- [ ] ¿Qué es pyang y cómo se usa para explorar modelos de datos?

### 2.3 YANG con NETCONF
- [ ] ¿Qué es NETCONF? ¿Bajo qué estándar fue creado?
- [ ] Cómo funcionan las comunicaciones NETCONF y por qué se crearon
- [ ] Protocolo que usa NETCONF por defecto para comunicarse con la red
- [ ] Cómo hacer una llamada NETCONF a un equipo de red: **ejemplo del comando + caso de uso**
- [ ] Qué es una RPC en NETCONF y qué formato de mensajes usa

### 2.4 YANG con RESTCONF
- [ ] ¿Qué es RESTCONF? Diferencia con NETCONF y su mayor ventaja
- [ ] Relación entre los modelos YANG y las llamadas de API vía RESTCONF
- [ ] Qué es POSTMAN, requerimientos de uso y cómo se usa para llamadas API
- [ ] Cómo hacer llamadas RESTCONF con POSTMAN **y** con Python
- [ ] **Al menos tres** herramientas de automatización de configuración de redes (push/pull de configuraciones). Para cada una:
  - [ ] ¿Método push o pull hacia los nodos finales?
  - [ ] Diseño del sistema central de gestión (master/slave, varios servidores, etc.)
  - [ ] Sistemas operativos donde puede usarse

---

## 3. Parte 2 — Caso de uso con POSTMAN o Python (3.2)

- [ ] Montar un caso de uso que **automatice algún proceso de administración de red** con POSTMAN o Python (3.2.1).
- [ ] Debe usar **NETCONF o RESTCONF** (no SNMP) (3.2.1).
- [ ] Debe pertenecer a una de estas áreas (3.2.2): **configuración** de dispositivos, **monitoreo** de dispositivos o **gestión de políticas**.

Ejemplos que da el enunciado (no limitantes):
- Configuración de dispositivos con scripts de Python o con Postman
- Configuración de varios dispositivos simultáneos
- Captura de alertas de interfaces con scripts/Python
- Integración de APIs entre herramientas de administración de red y de colaboración (p. ej. Webex)

Recursos permitidos (3.2.3): **developer.cisco.com** (módulos, laboratorios, código de ejemplo, sandboxes: Catalyst Center, Meraki Dashboard, Security Cloud Control, Catalyst SD-WAN, Webex, Ansible). También se puede usar cualquier sandbox de otros fabricantes.

---

## 4. Video (3.2.4)

| Requisito | Detalle |
|---|---|
| Duración | **No mayor a 10 minutos** |
| Participación | **Todas** las personas del grupo presentan una parte, **con cámara encendida** durante su parte |
| Introducción | Breve introducción del caso de uso: qué permite hacer |
| Requerimientos | Requerimientos mínimos de red y aplicaciones utilizadas |
| Implementación | Configuración requerida, scripts o programación utilizada |
| Utilidad real | Mostrar de forma clara, concreta y eficaz la utilidad del caso en la vida real |
| Formato sugerido | Breve presentación (diapositivas) + demostración práctica |
| Entrega | El **enlace** va dentro del informe |

### Rúbrica del video (9 pts = 50 % del proyecto)

| Objetivo | 3 pts | 2 pts | 1 pt |
|---|---|---|---|
| 1. Puntos del apartado 3.2.4 | Todos presentes | Entre 70 % y 95 % | Menos de 70 % |
| 2. Tiempo (10 min) | Se ajusta | Se pasa 10 % (hasta ~11 min) | Se pasa más de 20 % (más de 12 min) |
| 3. Demostración | Eficiente y sencilla | Casi completa, errores menores | No demuestra las características clave |

---

## 5. Informe final (4)

### 5.1 Secciones y puntaje (100 pts → 50 % del proyecto)

| # | Sección | Pts | Qué debe contener |
|---|---|---|---|
| 1 | Portada | 5 | — |
| 2 | Índice | 5 | — |
| 3 | Objetivos del Desafío | 5 | Primero los de la parte investigativa, luego los de la demostración del caso de uso |
| 4 | Investigación | 10 | Todos los temas del punto 3.1 (sección 2 de este documento) |
| 5 | Caso de Uso | 15 | Explicación detallada; problema seleccionado, solución escogida y herramientas usadas; lo más descriptivo posible; scripts o enlace al código (en Anexo 1); **enlace al video** |
| 6 | Resultados y Análisis | 5 | ¿Se logró la comunicación de red y el funcionamiento buscado? Resumen **detallado** (positivo o negativo). Validación cuantitativa si es posible: capturas de datos transmitidos, inputs/outputs, eficiencia |
| 7 | Conclusiones y Recomendaciones | 5 | ¿Qué funcionó y qué no de la parte práctica? ¿Qué mejoras se podrían hacer? |
| 8 | Referencias Bibliográficas | 5 | Formato **APA** |
| 9 | Anexo 1: Configuraciones o Código Fuente | 5 | Scripts, colecciones, configuraciones |
| 10 | Atributo: Conocimiento de Ingeniería | 20 | Rúbrica A (nivel 1–4): aplica conocimiento especializado para resolver el problema |
| 11 | Anexo 2: Trabajo Individual y en Equipo | 20 | Ver sección 7 de este documento |

### 5.2 Formato (4.3)

- [ ] Texto normal: **Arial 12**
- [ ] Títulos: **Arial 12 negrita**
- [ ] Párrafos **justificados** — **−1 punto de la nota final por cada página** con párrafos sin justificar
- [ ] Títulos de figuras, diagramas y tablas: **Arial 11**, nombre en negrita y descripción sin negrita. Ejemplo: **Tabla #1.** Direccionamiento IP Oficina X
- [ ] Ortografía y formato impecables
- [ ] Tamaño del informe: sin límite
- [ ] Entrega en **PDF**, una sola copia por grupo

---

## 6. Reglas de fuentes bibliográficas (4.3.5)

- [ ] **Todo** dato teórico debe estar fundamentado en una fuente y llevar su referencia.
- [ ] Fuentes de Internet deben ser confiables. **Wikipedia no se acepta.**
- [ ] Un dato teórico sin fuente → **se descuenta la mitad del puntaje de ese punto**.
- [ ] Formato APA.

Fuentes recomendables: RFC del IETF (3535, 6241 NETCONF, 8040 RESTCONF, 6020/7950 YANG), documentación de Cisco DevNet, documentación oficial de Postman/Ansible/Puppet/Chef/Salt, y los libros de la bibliografía del curso.

---

## 7. Anexo 2 — Trabajo Individual y en Equipo (7.2)

Documento titulado **"Trabajo individual y en equipo"**, adjunto como anexo del informe. Vale 20 pts del informe y se evalúa con los indicadores TE1–TE7 (escala 1–5 cada uno, 35 pts máx).

Debe incluir:

| # | Parte | Requisito |
|---|---|---|
| 1 | **Metas del proyecto** | Describir los entregables asociados |
| 2 | **Roles** | Roles y responsabilidades usados en el proyecto |
| 3 | **Reglas** | Reglas principales definidas para el trabajo en equipo |
| 4 | **Cronograma** | Actividades planeadas, **responsable** de cada una y **fechas** estimadas de entrega |
| 5 | **Minutas** | **Al menos tres reuniones** de trabajo evidenciadas, mostrando participación según rol y seguimiento al plan |
| 6 | **Bitácora** | De **cada integrante**: reuniones, investigaciones, consultas, etc. "Todo por más insignificante que sea" |
| 7 | **Evaluación de la eficiencia** | Cada estudiante completa **evaluación individual** y **coevaluación** en el formulario de Google (obligatorio, una sola vez, al finalizar el desafío) |

### Indicadores con que se califica

- **TE1** Estrategias equitativas e inclusivas en planificación, ejecución y evaluación
- **TE2** Planificación con roles, objetivos, metas, reglas y bitácoras
- **TE3** Acciones que promueven colaboración y cooperación
- **TE4** Ejecución de las estrategias planificadas
- **TE5** Evaluación de eficiencia y efectividad del desempeño
- **TE6** Evaluación de las estrategias de equidad e inclusión
- **TE7** Evaluación de las acciones de colaboración y cooperación

Niveles: 1 no cumple · 2 mínimo · 3 cumple con mejoras · 4 cumple · 5 excede expectativas.

> Para apuntar a 4–5 conviene que el anexo incluya, además de lo mínimo, una breve reflexión grupal sobre qué tan bien funcionaron las estrategias, la equidad en la repartición y la colaboración (TE5–TE7).

---

## 8. Riesgos que cuestan puntos

| Riesgo | Penalización |
|---|---|
| Página con párrafos sin justificar | −1 punto de la nota final **por página** |
| Dato teórico sin fuente | −50 % del puntaje de ese punto |
| Fuente no confiable (Wikipedia) | No se acepta |
| Video de más de 10 min | Baja a 2 pts (≈11 min) o 1 pt (>12 min) en el objetivo de tiempo |
| Alguien no aparece en el video o sin cámara | Incumple 3.2.4, afecta el objetivo 1 de la rúbrica |
| Menos de 3 minutas | Incumple el Anexo 2 |
| No llenar el formulario | Afecta la nota individual (TE5, TE6, TE7) |
| Olvidar el enlace del video en el informe | El video es el 50 % de la nota |
