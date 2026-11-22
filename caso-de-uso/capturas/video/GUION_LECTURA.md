# Guion de lectura — `demo_terminal_sin_audio.mp4`

Texto para **leer en voz alta** mientras corre el video de la demo (2:45, sin audio).
Cada bloque empieza en el segundo exacto en que aparece ese paso en pantalla y está pensado para leerse
a ritmo normal (≈ 2,5 palabras por segundo), de modo que termines un poco antes de que cambie la pantalla.

**Cómo usarlo:** en OBS (o en el editor de video) reproduce el MP4 a pantalla completa con tu cámara en una
esquina, y lee cada bloque cuando el reloj del video llegue a su marca. Lo que está en *cursiva entre
corchetes* son indicaciones, no se leen.

> Consejo: el último paso (YANG) queda fijo en pantalla desde 1:49 hasta 2:45. Puedes **cortar el video
> en 2:20** y usar el resto del tiempo para Postman o para pasar la palabra al siguiente integrante.

---

### 0:00 — Introducción *(pantalla en negro, 4 s)*

> Ahora vamos a ver el caso de uso funcionando sobre el router.

### 0:04 — Paso 1: conectividad RESTCONF *(9 s)*

> Primero comprobamos la conexión: con un GET al modelo ietf-interfaces, el router responde doscientos y
> devuelve en JSON sus interfaces.

### 0:13 — Paso 2: crear con PUT *(11 s)*

> Ahora configuramos. El script lee una lista de interfaces y, con una petición PUT por cada una, crea tres
> loopbacks. El router responde doscientos uno: creadas.

### 0:24 — Paso 3: verificar con GET *(10 s)*

> Verificamos la configuración con GET. Cada loopback aparece con su nombre, su descripción y su dirección IP,
> en formato JSON.

### 0:34 — Paso 4: modificar con PATCH *(10 s)*

> Con PATCH cambiamos solo la descripción de las tres, sin tocar lo demás. El código doscientos cuatro
> confirma el cambio.

### 0:44 — Paso 5: monitoreo *(9 s)*

> Pasamos al monitoreo. El script consulta el estado operativo de cada interfaz, y las tres están arriba.

### 0:53 — Paso 6: simular una falla *(10 s)*

> Para probar las alertas, simulamos una falla: apagamos la Loopback quinientos dos con un PATCH que pone
> enabled en falso.

### 1:03 — Paso 7: detección y alerta a Webex *(10 s)*

> El monitoreo detecta que la interfaz está caída y, por la API de Webex, envía una alerta a la sala del
> equipo. *[Si editas: aquí inserta 3–4 s de la captura `webex_alerta_interfaz_caida.jpg`.]*

### 1:13 — Paso 8: recuperar *(9 s)*

> Recuperamos la interfaz con otro PATCH, esta vez con enabled en verdadero.

### 1:22 — Paso 9: limpieza con DELETE *(16 s)*

> Y para terminar la parte de configuración, borramos las tres loopbacks con DELETE. El router queda
> exactamente como estaba. Todo esto, que por línea de comandos tomaría varios minutos equipo por equipo,
> se hizo en segundos.

### 1:38 — Paso 10: NETCONF *(11 s)*

> Por último, la misma información por NETCONF: abrimos una sesión SSH en el puerto ochocientos treinta y
> pedimos la configuración con la RPC get-config, que responde en XML.

### 1:49 — Paso 11: modelo YANG *(hasta 2:20 si cortas)*

> Todo esto funciona gracias a YANG. Este es el árbol del modelo ietf-interfaces generado con pyang: las
> ramas marcadas r w son configuración, y las r o son estado operativo, como el oper-status que usa el
> monitoreo. Las URL de RESTCONF siguen exactamente esta jerarquía.
>
> En resumen, el cien por ciento de las operaciones fueron exitosas, con tiempos de respuesta entre
> quince centésimas y dos coma siete segundos.

*[2:20 — corta aquí o continúa con Postman / pasa la palabra.]*

---

## Si el video se corta o algo falla

Las mismas pantallas están como imágenes en `capturas/terminal/01_…png` a `11_…png`: puedes mostrarlas
en orden y leer el mismo guion.
