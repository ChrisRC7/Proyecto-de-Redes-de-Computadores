# -*- coding: utf-8 -*-
"""Genera Informe.docx (Arial 12, todo justificado) a partir del contenido de este archivo y de los CSV reales."""
import csv, glob, os, re, statistics
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_COLOR_INDEX

BASE = os.path.dirname(os.path.abspath(__file__))
CASO = os.path.join(BASE, "..", "caso-de-uso")
J = WD_ALIGN_PARAGRAPH.JUSTIFY

doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21.59), Cm(27.94)
for m in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
    setattr(sec, m, Cm(2.54))


def fuente(style, size=12, bold=False):
    style.font.name = "Arial"
    style.font.size = Pt(size)
    style.font.bold = bold
    style.font.color.rgb = RGBColor(0, 0, 0)
    rpr = style.element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts"); rpr.append(rf)
    for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rf.set(qn(a), "Arial")
    for a in ("w:asciiTheme", "w:hAnsiTheme", "w:cstheme", "w:eastAsiaTheme"):
        if rf.get(qn(a)) is not None:
            del rf.attrib[qn(a)]


fuente(doc.styles["Normal"])
doc.styles["Normal"].paragraph_format.alignment = J
doc.styles["Normal"].paragraph_format.space_after = Pt(6)
doc.styles["Normal"].paragraph_format.line_spacing = 1.15
for n in (1, 2, 3):
    st = doc.styles[f"Heading {n}"]
    fuente(st, 12, True)
    st.paragraph_format.alignment = J
    st.paragraph_format.space_before = Pt(12)
    st.paragraph_format.space_after = Pt(6)
    st.paragraph_format.keep_with_next = True


def runs(p, texto, size=None, mono=False):
    """Admite **negrita** y [[resaltado]]."""
    for parte in re.split(r"(\*\*.+?\*\*|\[\[.+?\]\]|`[^`]+`)", texto):
        if not parte:
            continue
        if parte.startswith("**"):
            r = p.add_run(parte[2:-2]); r.bold = True
        elif parte.startswith("[["):
            r = p.add_run(parte[2:-2]); r.font.highlight_color = WD_COLOR_INDEX.YELLOW
        elif parte.startswith("`"):
            r = p.add_run(parte[1:-1]); r.font.name = "Courier New"
            r._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), "Courier New")
            r._element.rPr.rFonts.set(qn("w:hAnsi"), "Courier New")
            if size:
                r.font.size = Pt(size)
            continue
        else:
            r = p.add_run(parte)
        r.font.name = "Courier New" if mono else "Arial"
        if mono:
            r._element.rPr.rFonts.set(qn("w:ascii"), "Courier New")
        if size:
            r.font.size = Pt(size)
    return p


def P(texto, size=None, sangria=False):
    p = doc.add_paragraph()
    p.alignment = J
    if sangria:
        p.paragraph_format.left_indent = Cm(0.8)
    return runs(p, texto, size)


def H(texto, nivel=1):
    p = doc.add_heading(level=nivel)
    p.alignment = J
    r = p.add_run(texto); r.font.name = "Arial"; r.font.size = Pt(12); r.bold = True
    r.font.color.rgb = RGBColor(0, 0, 0)
    return p


def B(items):
    for it in items:
        p = doc.add_paragraph()
        p.alignment = J
        p.paragraph_format.left_indent = Cm(1.0)
        p.paragraph_format.first_line_indent = Cm(-0.5)
        runs(p, "• " + it)


def salto():
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


def pie(nombre, desc):
    p = doc.add_paragraph()
    p.alignment = J
    r = p.add_run(nombre + " "); r.bold = True; r.font.size = Pt(11); r.font.name = "Arial"
    r = p.add_run(desc); r.font.size = Pt(11); r.font.name = "Arial"
    return p


cont = {"Tabla": 0, "Figura": 0}


def tabla(desc, cab, filas, anchos=None, size=10):
    cont["Tabla"] += 1
    pie(f"Tabla #{cont['Tabla']}.", desc).paragraph_format.keep_with_next = True
    t = doc.add_table(rows=1, cols=len(cab))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, c in enumerate(cab):
        cel = t.rows[0].cells[i]; cel.text = ""
        pp = cel.paragraphs[0]; pp.alignment = J
        runs(pp, f"**{c}**", size)
        sh = OxmlElement("w:shd"); sh.set(qn("w:val"), "clear"); sh.set(qn("w:fill"), "D9D9D9")
        cel._tc.get_or_add_tcPr().append(sh)
    for f in filas:
        cells = t.add_row().cells
        for i, v in enumerate(f):
            cells[i].text = ""
            pp = cells[i].paragraphs[0]; pp.alignment = J
            runs(pp, str(v), size)
    if anchos:
        for row in t.rows:
            for i, w in enumerate(anchos):
                row.cells[i].width = Cm(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def figura(ruta, desc, ancho=15.5):
    cont["Figura"] += 1
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(ruta, width=Cm(ancho))
    pie(f"Figura #{cont['Figura']}.", desc)


def codigo(texto):
    for linea in texto.strip("\n").split("\n"):
        p = doc.add_paragraph(); p.alignment = J
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.left_indent = Cm(0.4)
        runs(p, linea if linea else " ", 8.5, mono=True)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


# ---------------------------------------------------------------- datos reales
def leer(patron):
    filas = []
    for f in sorted(glob.glob(os.path.join(CASO, "resultados", patron))):
        with open(f, encoding="utf-8") as fh:
            filas += list(csv.DictReader(fh))
    return filas


cfg = leer("configuracion_*.csv")
por_accion = {}
for r in cfg:
    por_accion.setdefault(r["accion"], []).append(r)
orden = ["crear", "listar", "modificar", "apagar", "encender", "borrar"]
http_esp = {"crear": "201 (PUT)", "listar": "200 (GET)", "modificar": "204 (PATCH)",
            "apagar": "204 (PATCH)", "encender": "204 (PATCH)", "borrar": "204 (DELETE)"}
filas_cfg = []
for a in orden:
    rs = por_accion.get(a, [])
    if not rs:
        continue
    t = [float(x["tiempo_ms"]) for x in rs]
    ok = sum(1 for x in rs if x["http"].startswith("2"))
    filas_cfg.append([a, http_esp[a], len(rs), f"{ok}/{len(rs)}", f"{min(t):.0f}", f"{statistics.mean(t):.0f}", f"{max(t):.0f}"])
total_ops = len(cfg)
total_ok = sum(1 for x in cfg if x["http"].startswith("2"))
todos_t = [float(x["tiempo_ms"]) for x in cfg]

mon = leer("monitoreo.csv")
corridas = {}
for r in mon:
    corridas.setdefault(r["fecha"], []).append(r)
filas_mon = []
for fch, rs in corridas.items():
    caidas = [x["interfaz"] for x in rs if x["oper"] != "up" or x["admin"] != "up"]
    filas_mon.append([fch.replace("T", " "), len(rs), f"{float(rs[0]['tiempo_estado_ms']):.0f}",
                      f"{float(rs[0]['tiempo_config_ms']):.0f}", ", ".join(caidas) if caidas else "ninguna"])

CAP = os.path.join(CASO, "capturas")
TER = os.path.join(CAP, "terminal")

# ---------------------------------------------------------------- PORTADA
for _ in range(3):
    doc.add_paragraph()
for t in ["Instituto Tecnológico de Costa Rica", "Escuela de Ingeniería en Computadores",
          "CE-5301 Redes de Computadoras", "II Semestre 2026"]:
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    runs(p, f"**{t}**")
for _ in range(2):
    doc.add_paragraph()
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
runs(p, "**Desafío de Redes**")
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
runs(p, "Configuración y monitoreo de interfaces de un router Cisco IOS XE mediante RESTCONF, con alertas a Webex")
for _ in range(2):
    doc.add_paragraph()
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
runs(p, "**Integrantes**")
for n in ["Christopher David Rodríguez Cordero, carné 2022040771", "Randall Bolaños López, carné 2019043784",
          "Javier Tenorio Cervantes, carné 2020065308"]:
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; runs(p, n)
runs(doc.paragraphs[-1], "")
for _ in range(1):
    doc.add_paragraph()
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
runs(p, "Profesor: Rodolfo Tacsan Chaves")
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
runs(p, "Fecha de entrega: 26 de noviembre de 2026")
salto()

# ---------------------------------------------------------------- ÍNDICE
p0 = doc.add_paragraph(); runs(p0, "**Índice**")
p = doc.add_paragraph()
r = p.add_run()
for tipo, txt in (("begin", None), (None, ' TOC \\o "1-2" \\h \\z \\u '), ("separate", None), ("end", None)):
    if tipo:
        e = OxmlElement("w:fldChar"); e.set(qn("w:fldCharType"), tipo); r._r.append(e)
    else:
        e = OxmlElement("w:instrText"); e.set(qn("xml:space"), "preserve"); e.text = txt; r._r.append(e)
salto()

# ---------------------------------------------------------------- OBJETIVOS
H("1. Objetivos del Desafío")
H("1.1 Objetivos de la parte investigativa", 2)
B([
    "Explicar qué es la programabilidad basada en modelos y por qué surgió, a partir del trabajo de los equipos de DevOps, las limitaciones de SNMP y los requisitos del RFC 3535.",
    "Describir el lenguaje YANG, la estructura de sus modelos de datos y el uso de pyang para explorarlos.",
    "Describir el protocolo NETCONF (estándar, transporte, RPC y formato de mensajes) con un ejemplo de llamada a un equipo real.",
    "Describir el protocolo RESTCONF, su diferencia con NETCONF, su relación con YANG y su uso con Postman y con Python.",
    "Comparar al menos tres herramientas de automatización de la configuración de redes según su método (push o pull), el diseño de su sistema central y los sistemas operativos en que funcionan.",
])
H("1.2 Objetivos de la demostración del caso de uso", 2)
B([
    "Automatizar la creación, modificación, apagado y borrado de interfaces de un router Cisco IOS XE mediante RESTCONF, con Postman y con scripts de Python, incluyendo configuración masiva de varias interfaces.",
    "Monitorear el estado operativo de las interfaces mediante RESTCONF y detectar las que estén caídas.",
    "Integrar la API de Webex para enviar una alerta automática a una sala cuando una interfaz esté caída.",
    "Validar cuantitativamente el funcionamiento (códigos HTTP, tiempos de respuesta y tasa de éxito) y demostrar su utilidad real en un video de máximo diez minutos.",
])
salto()

# ---------------------------------------------------------------- INVESTIGACIÓN
H("2. Investigación")
# ---- Bloque A (Randall): programabilidad basada en modelos
H("2.1 ¿Qué es y por qué la programabilidad basada en modelos?", 2)
H("2.1.1 ¿Qué hace un equipo de DevOps?", 3)
P("DevOps es la combinación de filosofías culturales, prácticas y herramientas que aumenta la capacidad de una organización para entregar aplicaciones y servicios a alta velocidad. En este modelo, los equipos de desarrollo y de operaciones dejan de trabajar aislados: participan juntos en todo el ciclo de vida del servicio, desde el desarrollo y las pruebas hasta la implementación y la operación (Amazon Web Services, s. f.).")
P("Un equipo de DevOps automatiza los procesos que antes eran manuales y lentos, y se apoya en prácticas como las siguientes (Amazon Web Services, s. f.):")
B([
    "**Integración y entrega continuas:** los cambios se integran, se prueban y se despliegan con frecuencia y de forma automática.",
    "**Infraestructura como código:** la infraestructura se describe en archivos de texto versionados y se aprovisiona con herramientas, no a mano.",
    "**Monitoreo y registro:** se miden las métricas y los registros de las aplicaciones y de la infraestructura para reaccionar a tiempo.",
    "**Comunicación y colaboración:** herramientas y hábitos que comparten la información entre los equipos.",
])
P("En redes, aplicar estas prácticas exige que los equipos se puedan configurar y consultar por medio de APIs y no solo por la CLI, que es la base de la automatización de redes que promueve Cisco DevNet (Cisco Systems, s. f.-a). El caso de uso de este proyecto sigue esa idea: la configuración de las interfaces está en un archivo (`interfaces.json`) dentro de un repositorio de Git y se aplica con un script.")
H("2.1.2 Rol de SNMP", 3)
P("SNMP (Simple Network Management Protocol) es el protocolo con el que tradicionalmente se gestionan los equipos de red. Sigue un modelo de gestor y agente: una estación de gestión consulta o modifica las variables que cada agente expone en su MIB (Management Information Base) con las operaciones GetRequest, GetNextRequest y SetRequest, y el agente puede enviar avisos no solicitados (Trap). Los mensajes viajan sobre UDP: el agente recibe las peticiones en el puerto 161 y los traps se reciben en el puerto 162 (Case et al., 1990).")
P("Su papel principal ha sido el **monitoreo**. En 2002, el IAB observó que SNMP funciona razonablemente bien para vigilar equipos y que está ampliamente desplegado para eso, pero que se usa poco para **configurarlos**. Los operadores dieron varias razones: muchos módulos MIB estándar no tienen objetos de escritura, el rendimiento es pobre al recuperar grandes volúmenes de datos (como las tablas de enrutamiento), su modelo de transacciones es difícil de implementar y no hay una forma sencilla de guardar y restaurar configuraciones. Por eso la configuración se seguía haciendo por CLI, que es cómoda para una persona pero difícil de automatizar y carece de un modelo de datos común. El mismo taller concluyó que eliminar SNMP no era una opción, pues sigue siendo útil para el monitoreo (Schönwälder, 2003).")
H("2.1.3 ¿Qué es el RFC 3535?", 3)
P("El RFC 3535, “Overview of the 2002 IAB Network Management Workshop”, es un documento informativo publicado en mayo de 2003 que resume el taller sobre gestión de redes que el IAB (Internet Architecture Board) organizó del 4 al 6 de junio de 2002 en Reston, Virginia. El taller reunió a operadores de red y a desarrolladores de protocolos para revisar el estado de la gestión de redes y orientar el trabajo futuro del IETF (Schönwälder, 2003).")
P("Su aporte más conocido es la lista de 14 requisitos de los operadores para la gestión de la configuración. Entre ellos (Schönwälder, 2003):")
B([
    "La facilidad de uso es un requisito clave.",
    "Separar con claridad los datos de configuración, el estado operativo y las estadísticas, y poder obtener cada uno por aparte.",
    "Configurar la red como un todo y no equipo por equipo, con transacciones que abarquen varios dispositivos.",
    "Respaldar y restaurar configuraciones como una operación estándar, y poder compararlas con herramientas de texto (diff y control de versiones).",
    "Distinguir entre distribuir una configuración y activarla, de modo que un equipo pueda guardar varias configuraciones.",
    "Un control de acceso con la granularidad de las operaciones, basado en roles.",
])
P("Entre sus recomendaciones, el taller pidió al IETF concentrar recursos en estandarizar mecanismos de gestión de la configuración y en tecnologías basadas en XML para configurar equipos (Schönwälder, 2003). A partir de esas observaciones se formó el grupo de trabajo NETCONF, que creó el protocolo del mismo nombre; después, el grupo NETMOD definió YANG como el lenguaje para modelar los datos que maneja NETCONF (Shafer, 2011).")
H("2.1.4 Definición de programabilidad basada en modelos", 3)
P("La programabilidad basada en modelos (Model-Driven Programmability) es una forma de gestionar los equipos de red en la que la configuración y los datos operativos se leen y se escriben por medio de una API estándar, cuya estructura la definen modelos de datos escritos en YANG. El modelo indica qué datos existen, de qué tipo son y qué restricciones cumplen; el protocolo (NETCONF, RESTCONF o gNMI) solo transporta esos datos (Cisco Systems, s. f.-b).")
P("A diferencia de la CLI, el equipo recibe y devuelve datos estructurados que una máquina puede validar, y no texto pensado para personas. A diferencia de SNMP, el mismo modelo sirve para configurar y para monitorear, y el protocolo ofrece operaciones como validar o bloquear la configuración antes de cambiarla (Enns et al., 2011). Así se atienden varios de los requisitos del RFC 3535, como separar la configuración del estado y manejar transacciones (Shafer, 2011).")
H("2.1.5 Bloques básicos de construcción", 3)
P("La programabilidad basada en modelos se organiza en cuatro bloques que se apoyan uno sobre otro (Cisco Systems, s. f.-b):")
tabla("Bloques básicos de la programabilidad basada en modelos.", ["Bloque", "Función", "Ejemplos", "En este proyecto"], [
    ["Modelos de datos", "Definen la estructura, los tipos y las restricciones de los datos", "Modelos YANG del IETF, de OpenConfig y nativos de cada fabricante", "ietf-interfaces e ietf-ip"],
    ["Protocolos", "Definen las operaciones para leer y escribir los datos", "NETCONF, RESTCONF y gNMI", "RESTCONF (Postman y Python) y NETCONF (ncclient)"],
    ["Codificación", "Formato en que viajan los datos", "XML y JSON", "JSON en RESTCONF y XML en NETCONF"],
    ["Transporte", "Canal seguro entre el cliente y el equipo", "SSH, HTTPS y gRPC sobre HTTP/2", "HTTPS (puerto 443) y SSH (puerto 830)"],
], [3.5, 4.2, 4.1, 3.8])
P("Cada protocolo tiene su propia especificación: NETCONF usa mensajes XML sobre SSH (Enns et al., 2011; Wasserman, 2011) y RESTCONF usa HTTPS con XML o JSON (Bierman et al., 2017). La codificación en JSON de los datos modelados con YANG está definida en el RFC 7951 (Lhotka, 2016).")
H("2.1.6 ¿Qué es un modelo de datos?", 3)
P("El RFC 3444 distingue dos niveles. Un **modelo de información** describe los objetos gestionados a nivel conceptual, sin depender de una implementación ni de un protocolo, y está pensado para diseñadores y operadores. Un **modelo de datos** describe esos objetos con un nivel de abstracción menor y con muchos más detalles: está pensado para quien implementa e incluye construcciones propias del protocolo, como las reglas para mapear los objetos a los mensajes. Los módulos MIB escritos en SMI son un ejemplo clásico de modelo de datos (Pras & Schönwälder, 2003).")
P("En la gestión de redes actual, un modelo de datos es el esquema que define qué datos de configuración y de estado expone un equipo, cómo se organizan jerárquicamente, de qué tipo es cada uno y qué valores son válidos. Por ejemplo, el modelo `ietf-interfaces` define una lista de interfaces identificadas por su nombre, cada una con su descripción, su tipo y un indicador de si está habilitada (Bjørklund, 2018a). Como el modelo es común, un mismo script puede configurar equipos distintos que lo implementen sin depender de la sintaxis de la CLI de cada uno.")

# ---- Bloque B (Randall): YANG
H("2.2 Introducción a YANG", 2)
H("2.2.1 ¿Qué es YANG?", 3)
P("YANG es un lenguaje de modelado de datos que se usa para modelar los datos de configuración, los datos de estado, las operaciones remotas (RPC) y las notificaciones de los protocolos de gestión de red (Bjørklund, 2016). La primera versión se publicó en el RFC 6020 como el lenguaje de modelado de NETCONF (Bjørklund, 2010), y la versión vigente, YANG 1.1, en el RFC 7950 (Bjørklund, 2016).")
P("Los modelos YANG se escriben en módulos de texto legibles por personas y organizan los datos como un árbol jerárquico. El lenguaje no depende del protocolo: los datos que describe se pueden codificar en XML (Bjørklund, 2016) o en JSON (Lhotka, 2016) y se pueden transportar con NETCONF o con RESTCONF (Bierman et al., 2017).")
H("2.2.2 Lenguaje YANG, modelos de datos YANG y YANG data", 3)
P("Los tres términos se refieren a niveles distintos, de forma parecida a un lenguaje de programación, un programa escrito en él y los datos que ese programa maneja (Bjørklund, 2016, 2018a; Lhotka, 2016):")
tabla("Diferencia entre lenguaje YANG, modelos de datos YANG y YANG data.", ["Término", "Qué es", "Ejemplo en este proyecto"], [
    ["Lenguaje YANG", "La gramática: las sentencias (module, container, list, leaf, type, augment, etc.) y sus reglas, definidas en el RFC 7950", "Las sentencias con las que está escrito ietf-interfaces"],
    ["Modelo de datos YANG", "Un módulo escrito en YANG que define la estructura de un conjunto de datos; lo publican el IETF, OpenConfig o los fabricantes", "ietf-interfaces (RFC 8343) e ietf-ip (RFC 8344)"],
    ["YANG data", "Los datos concretos de un equipo (instancias) que cumplen con un modelo, codificados en XML o JSON", "La Loopback501 con su descripción y su dirección 10.150.1.1"],
], [4.0, 6.6, 5.0])
P("El siguiente extracto simplificado del modelo `ietf-interfaces` está escrito en lenguaje YANG (Bjørklund, 2018a):")
codigo("""
module ietf-interfaces {
  namespace "urn:ietf:params:xml:ns:yang:ietf-interfaces";
  prefix if;
  container interfaces {
    list interface {
      key "name";
      leaf name        { type string; }
      leaf description { type string; }
      leaf type        { type identityref { base interface-type; } mandatory true; }
      leaf enabled     { type boolean; default "true"; }
    }
  }
}
""")
P("Y este es un ejemplo de YANG data: el cuerpo JSON que el script `configurar_interfaces.py` envía con PUT para crear la Loopback501. Cada nombre lleva el prefijo del módulo que lo define cuando cambia de módulo (Lhotka, 2016); por eso `ietf-ip:ipv4` indica que ese contenedor viene del modelo `ietf-ip`, que lo agrega a cada interfaz (Bjørklund, 2018b):")
codigo("""
{
  "ietf-interfaces:interface": {
    "name": "Loopback501",
    "description": "CE5301 - creada por RESTCONF",
    "type": "iana-if-type:softwareLoopback",
    "enabled": true,
    "ietf-ip:ipv4": {
      "address": [{"ip": "10.150.1.1", "netmask": "255.255.255.255"}]
    }
  }
}
""")
H("2.2.3 Estructura del modelo de datos YANG y cómo se usa", 3)
P("Un módulo YANG tiene un encabezado y un cuerpo con las definiciones (Bjørklund, 2016):")
B([
    "**Encabezado:** el nombre del módulo, su `namespace` (identificador único usado en XML), su `prefix`, las sentencias `import` de otros módulos, la organización, el contacto, la descripción y las revisiones con su fecha.",
    "**Nodos de datos:** `container` agrupa nodos relacionados; `list` es una secuencia de entradas identificadas por una llave (`key`); `leaf` guarda un valor simple, y `leaf-list` guarda varios valores del mismo tipo.",
    "**Tipos:** tipos base (`string`, `boolean`, `int32`, `enumeration`, `identityref`, etc.) y tipos derivados definidos con `typedef`.",
    "**Reutilización y extensión:** `grouping` y `uses` reutilizan conjuntos de nodos, y `augment` agrega nodos a otro módulo. Así, `ietf-ip` agrega los contenedores `ipv4` e `ipv6` a cada interfaz de `ietf-interfaces` (Bjørklund, 2018b).",
    "**Configuración y estado:** `config true` marca los datos de configuración, que se pueden leer y escribir, y `config false` marca los datos de estado, que solo se leen, como `oper-status`.",
    "**Operaciones y eventos:** `rpc` y `action` definen operaciones, y `notification` define los avisos que envía el equipo.",
    "**Partes opcionales:** `feature` e `if-feature` marcan partes del modelo que un equipo puede implementar o no.",
])
P("**Cómo se usa:** el equipo anuncia qué módulos implementa; en NETCONF lo hace al abrir la sesión, con las capacidades del mensaje `<hello>` y la biblioteca YANG (`yang-library`) (Bjørklund, 2016), como se vio con el router del sandbox en la sección 2.3.4. Con el modelo, el cliente sabe qué datos puede pedir y cómo debe escribirlos. La ruta del árbol se traduce directamente en la petición. En RESTCONF, el contenedor `interfaces` y la entrada `Loopback501` de la lista se convierten en este URL (Bierman et al., 2017):")
codigo("https://10.10.20.48/restconf/data/ietf-interfaces:interfaces/interface=Loopback501")
P("En NETCONF, el `namespace` del módulo se usa en el filtro XML del `get-config`. En ambos casos, el equipo valida los datos contra el modelo y rechaza los que no cumplen sus tipos o restricciones (Bjørklund, 2016).")
H("2.2.4 ¿Qué es pyang y cómo se usa?", 3)
P("pyang es una herramienta de código abierto escrita en Python que valida módulos YANG, los transforma a otros formatos y genera código a partir de ellos (Bjørklund, s. f.). Se instala con `pip install pyang` y se usa desde la línea de comandos con la forma `pyang [opciones] modulo.yang`:")
tabla("Opciones comunes de pyang.", ["Opción", "Para qué sirve"], [
    ["(sin opciones)", "Valida el módulo y reporta errores y advertencias"],
    ["`-f tree`", "Muestra el módulo como árbol, con la notación del RFC 8340"],
    ["`-f tree --tree-depth 3`", "Limita la profundidad del árbol"],
    ["`-f tree --tree-path /interfaces/interface`", "Muestra solo una rama del árbol"],
    ["`-f sample-xml-skeleton`", "Genera un esqueleto XML de datos de ejemplo"],
    ["`-p carpeta`", "Indica dónde buscar los módulos importados"],
], [8.6, 7.0], 9)
P("En este proyecto se usó pyang 2.7.1 con los módulos `ietf-interfaces` (revisión 2018-02-20) e `ietf-ip` (revisión 2018-02-22). Este es el inicio del árbol de `ietf-interfaces`:")
codigo("""
> pyang -f tree ietf-interfaces.yang
module: ietf-interfaces
  +--rw interfaces
  |  +--rw interface* [name]
  |     +--rw name                        string
  |     +--rw description?                string
  |     +--rw type                        identityref
  |     +--rw enabled?                    boolean
  |     +--rw link-up-down-trap-enable?   enumeration {if-mib}?
  |     +--ro admin-status                enumeration {if-mib}?
  |     +--ro oper-status                 enumeration
  |     ...
  x--ro interfaces-state
     x--ro interface* [name]
        ...
""")
P("En el árbol, cada línea es un nodo y la sangría muestra la jerarquía. `rw` indica datos de configuración y `ro`, datos de estado; `*` marca una lista y entre corchetes va su llave; `?` marca un nodo opcional; `{if-mib}?` indica que el nodo depende de una función opcional, y `x` marca un nodo obsoleto (deprecated). Los nodos que vienen de otro módulo llevan su prefijo, como `ip:ipv4` cuando se carga también `ietf-ip` (Bjørklund & Berger, 2018).")
P("El árbol sirvió para diseñar el caso de uso: muestra que `name`, `description`, `type` y `enabled` se pueden escribir (`rw`), por lo que se crean y modifican con PUT y PATCH, y que `oper-status` es de solo lectura (`ro`), por lo que el monitoreo solo lo consulta. También muestra que `interfaces-state` está obsoleto (Bjørklund, 2018a), aunque el IOS XE 17.12 del sandbox lo sigue publicando y el script de monitoreo lo usa.")
figura(os.path.join(TER, "11_yang.png"), "Árbol del modelo ietf-interfaces generado con pyang; la rama interfaces-state aparece marcada como obsoleta (x).", 15.0)

H("2.3 YANG con NETCONF", 2)
H("2.3.1 ¿Qué es NETCONF y bajo qué estándar fue creado?", 3)
P("NETCONF (Network Configuration Protocol) es un protocolo que permite instalar, manipular y borrar la configuración de dispositivos de red. Fue estandarizado por el IETF en el RFC 6241 (Enns et al., 2011), que actualiza el RFC 4741 original. Sus operaciones usan un mecanismo de llamadas a procedimiento remoto (RPC) con mensajes codificados en XML.")
H("2.3.2 Cómo funcionan las comunicaciones y por qué se crearon", 3)
P("NETCONF funciona con un modelo cliente-servidor por capas: contenido, operaciones, mensajes (RPC) y transporte seguro (Enns et al., 2011). Al abrir la sesión, ambos extremos intercambian un mensaje `<hello>` con sus capacidades (capabilities); luego el cliente envía `<rpc>` y el servidor responde con `<rpc-reply>`. Los datos se organizan en almacenes de configuración (`running`, `candidate`, `startup`) y el protocolo distingue entre configuración y estado. NETCONF se creó para atender las carencias señaladas en el RFC 3535: ofrecer transacciones, separación entre configuración y estado, y una interfaz programática confiable que SNMP no brindaba para configurar (Schönwälder, 2003; Enns et al., 2011).")
H("2.3.3 Protocolo de transporte por defecto", 3)
P("El transporte obligatorio de NETCONF es SSH, en el puerto TCP 830 (Wasserman, 2011). En el router del sandbox el puerto 830 está habilitado, como lo muestra la sesión de la Figura #2.")
H("2.3.4 Ejemplo de llamada NETCONF y caso de uso", 3)
P("El script `netconf_ejemplo.py` usa la biblioteca ncclient para abrir una sesión NETCONF contra el router y pedir la configuración de las interfaces con la operación `get-config` sobre el almacén `running`, filtrada con el modelo `ietf-interfaces`:")
codigo("""
from ncclient import manager
FILTRO = '<filter><interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces"/></filter>'
with manager.connect(host="10.10.20.48", port=830, username=USUARIO, password=CLAVE,
                     hostkey_verify=False, device_params={"name": "iosxe"}) as m:
    respuesta = m.get_config(source="running", filter=FILTRO)
""")
P("**Caso de uso:** obtener en XML la configuración de todas las interfaces del router sin entrar por CLI. En la prueba del 22 de noviembre de 2026, la sesión se abrió en 2 764 ms (id de sesión 42) y la operación `get-config` respondió en 389 ms; el servidor anunció las capacidades `base:1.0`, `base:1.1`, `writable-running`, `validate`, `xpath` y `yang-library`, entre otras (Figura #2).")
figura(os.path.join(TER, "10_netconf.png"), "Sesión NETCONF y operación get-config ejecutadas con ncclient contra el Catalyst 8000v.", 15.5)
H("2.3.5 ¿Qué es una RPC y qué formato de mensajes usa?", 3)
P("Una RPC (Remote Procedure Call, llamada a procedimiento remoto) es un mecanismo por el cual un cliente solicita que el servidor ejecute una operación y devuelva el resultado. En NETCONF, el cliente envía un elemento `<rpc>` con un atributo `message-id` que contiene la operación (`<get-config>`, `<edit-config>`, `<get>`, `<commit>`, etc.), y el servidor contesta con un `<rpc-reply>` con el mismo `message-id`, que incluye los datos, `<ok/>` o un `<rpc-error>`. Todos los mensajes están codificados en XML (Enns et al., 2011).")
codigo("""
<rpc message-id="101" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <get-config>
    <source><running/></source>
    <filter><interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces"/></filter>
  </get-config>
</rpc>
""")

# ---- Bloque D (asignado a Javier; borrador para su revisión): RESTCONF y herramientas
H("2.4 YANG con RESTCONF", 2)
H("2.4.1 ¿Qué es RESTCONF? Diferencia con NETCONF y su mayor ventaja", 3)
P("RESTCONF es un protocolo basado en HTTP que ofrece una interfaz programática para acceder a los datos definidos en YANG, usando los mismos conceptos de almacenes de datos (datastores) que NETCONF. Fue estandarizado por el IETF en el RFC 8040, en enero de 2017. Sus operaciones usan los métodos de HTTP (GET, POST, PUT, PATCH y DELETE) sobre recursos identificados por un URL, los datos viajan codificados en XML o en JSON con los tipos de medio `application/yang-data+xml` y `application/yang-data+json`, y el protocolo debe usarse siempre sobre TLS, es decir, con HTTPS (Bierman et al., 2017).")
P("RESTCONF no pretende reemplazar a NETCONF, sino ofrecer una "
  "alternativa más sencilla para acceder a los datos de configuración "
  "y estado mediante HTTP. En su especificación original, RFC 8040, "
  "presenta una vista unificada de los datos y no proporciona operaciones "
  "de bloqueo explícito ni confirmación manual de los cambios. "
  "Si el equipo dispone de un almacén `candidate`, las modificaciones "
  "exitosas se confirman automáticamente en `running` "
  "(Bierman et al., 2017). Posteriormente, el RFC 8527 amplió RESTCONF "
  "para permitir el acceso a almacenes de datos específicos en equipos "
  "compatibles con la arquitectura NMDA (Bjørklund et al., 2019). "
  "La siguiente tabla resume las diferencias:")
tabla("Comparación entre NETCONF y RESTCONF.", ["Aspecto", "NETCONF", "RESTCONF"], [
    ["Estándar", "RFC 6241 (2011)", "RFC 8040 (2017)"],
    ["Transporte", "SSH, puerto TCP 830", "HTTPS (HTTP sobre TLS), puerto TCP 443"],
    ["Codificación", "XML", "XML o JSON"],
    ["Sesión", "Con estado: se abre una sesión y se intercambian capacidades con `<hello>`", "Sin estado: cada petición HTTP es independiente"],
    ["Operaciones", "RPC en XML: `get`, `get-config`, `edit-config`, `lock`, `commit`, etc.", "Métodos HTTP sobre un URL: GET, POST, PUT, PATCH y DELETE"],
    ["Almacenes y bloqueo",
     "Acceso a almacenes según las capacidades del equipo; bloqueo y confirmación explícita cuando corresponde",
     "Vista unificada en RFC 8040; acceso a almacenes específicos mediante RFC 8527; sin bloqueo explícito"],
    ["Clientes típicos", "Bibliotecas como ncclient", "Cualquier cliente HTTP: Postman, curl o requests"],
], [3.8, 5.9, 5.9])
P("Fuentes de la tabla: Enns et al. (2011), Wasserman (2011), Bierman et al. (2017) y Bjørklund et al. (2019).", 11)
P("**Mayor ventaja:** su sencillez. Como usa HTTP con un estilo REST, cualquier herramienta o lenguaje que sepa hacer peticiones web puede gestionar el equipo, sin abrir sesiones ni manejar XML si se prefiere JSON (Bierman et al., 2017). En este proyecto eso permitió usar el mismo router desde Postman y desde Python con muy poco código; a cambio, cuando se necesitan transacciones con bloqueo o varios almacenes, NETCONF sigue siendo la opción adecuada.")
H("2.4.2 Relación entre los modelos YANG y las llamadas API RESTCONF", 3)
P("En RESTCONF, el modelo YANG define la API. El cliente descubre la raíz con `/.well-known/host-meta`, que normalmente apunta a `/restconf`; debajo están los recursos `data` (configuración y estado), `operations` (las RPC definidas en los modelos) y `yang-library-version`. El URL de un dato se forma con la ruta de su árbol YANG: el primer nodo lleva el nombre del módulo como prefijo (`ietf-interfaces:interfaces`) y la entrada de una lista se indica con `=` y el valor de su llave (`interface=Loopback501`) (Bierman et al., 2017). El cuerpo de la petición es YANG data codificado en JSON o XML (Lhotka, 2016).")
codigo("https://10.10.20.48/restconf/data/ietf-interfaces:interfaces/interface=Loopback501")
B([
    "`https://10.10.20.48/restconf`: raíz de RESTCONF del equipo.",
    "`/data`: recurso con los datos de configuración y de estado.",
    "`/ietf-interfaces:interfaces`: módulo YANG y su contenedor.",
    "`/interface=Loopback501`: lista `interface` y valor de su llave `name`.",
])

P("Los métodos HTTP de RESTCONF permiten realizar operaciones "
  "equivalentes a las principales operaciones de NETCONF sobre "
  "los datos definidos por YANG (Bierman et al., 2017):")

tabla("Métodos de RESTCONF y su equivalente en NETCONF.",
      ["Método", "Operación NETCONF", "Uso en este proyecto", "Respuesta HTTP"], [
    ["GET", "`get-config` o `get`",
     "Listar interfaces y leer su estado", "200"],

    ["POST", "`edit-config` (create) o invocar una RPC",
     "No utilizado directamente sobre RESTCONF", "201 al crear"],

    ["PUT", "`edit-config` (create o replace)",
     "Crear las interfaces Loopback", "201 / 204"],

    ["PATCH", "`edit-config` (merge, para plain patch)",
     "Cambiar la descripción, apagar y encender", "204"],

    ["DELETE", "`edit-config` (delete)",
     "Borrar las interfaces", "204"],
], [2.0, 4.6, 6.2, 2.8])

P("Fuente: Bierman et al. (2017).", 11)

P("En este proyecto, el método POST también se utiliza para "
  "enviar mensajes de alerta a Webex mediante su API REST, "
  "obteniendo una respuesta HTTP 200. Esta operación es independiente "
  "de RESTCONF y permite integrar la administración de redes con "
  "una herramienta de comunicación y colaboración (Webex, s. f.).")

H("2.4.3 ¿Qué es Postman? Requerimientos y uso para llamadas API", 3)
P("Postman es una plataforma para diseñar, probar y documentar APIs. Permite armar peticiones HTTP indicando el método, el URL, los encabezados, la autenticación y el cuerpo, ver la respuesta con su código y su tiempo, y guardar las peticiones en colecciones. Las colecciones usan variables de entorno, pueden incluir pruebas escritas en JavaScript que validan cada respuesta y se pueden ejecutar completas con el Collection Runner o desde la línea de comandos con Newman (Postman, s. f.).")

P("**Requerimientos** para usar Postman con RESTCONF:")

B([
    "Postman instalado como aplicación de escritorio para Windows, "
    "macOS o Linux. También puede utilizarse la versión web con "
    "Postman Desktop Agent para acceder a recursos de redes privadas "
    "(Postman, s. f.).",

    "Conectividad IP entre el cliente y el dispositivo de red. "
    "En este proyecto se requiere establecer una conexión VPN "
    "hacia el sandbox de Cisco.",

    "Servicio RESTCONF habilitado en el equipo y acceso al puerto "
    "TCP 443. En Cisco IOS XE se habilita mediante los comandos "
    "`restconf` e `ip http secure-server` "
    "(Cisco Systems, s. f.-b).",

    "Credenciales válidas de un usuario autorizado para consultar "
    "y modificar la configuración del dispositivo, según las "
    "políticas de autenticación y autorización AAA "
    "(Cisco Systems, s. f.-b).",

    "Un certificado TLS confiable para establecer una comunicación "
    "HTTPS segura. En el ambiente controlado del laboratorio se "
    "deshabilitó temporalmente la verificación del certificado debido "
    "al uso de un certificado autofirmado. En producción se recomienda "
    "utilizar certificados válidos y mantener habilitada su "
    "verificación (Postman, s. f.).",
])

P("**Uso:** se crea una petición, se elige el método, se escribe el URL de RESTCONF, se configura la autenticación básica (usuario y contraseña) y se agregan los encabezados `Accept` y `Content-Type` con el valor `application/yang-data+json`; en PUT y PATCH se agrega el cuerpo JSON. Al enviarla, Postman muestra el código HTTP, el tiempo y el cuerpo de la respuesta.")
H("2.4.4 Llamadas RESTCONF con Postman y con Python", 3)
P("**Con Postman:** la colección del proyecto (sección 3.5) contiene las diez peticiones del caso de uso. Esta es la configuración de la petición que crea una interfaz:")
tabla("Configuración en Postman de la petición que crea la Loopback501.", ["Campo", "Valor"], [
    ["Método", "PUT"],
    ["URL", "`https://{{host}}/restconf/data/ietf-interfaces:interfaces/interface=Loopback501`"],
    ["Autorización", "Basic Auth con las variables `{{username}}` y `{{password}}`"],
    ["Encabezados", "`Accept` y `Content-Type`: `application/yang-data+json`"],
    ["Cuerpo (raw, JSON)", "El YANG data de la sección 2.2.2"],
    ["Prueba", "El código de respuesta es 2xx y el tiempo es menor a 5 s"],
    ["Respuesta esperada", "201 Created (o 204 si la interfaz ya existía)"],
], [4.0, 11.6], 9)

P("**Con Python:** se utiliza la biblioteca requests para enviar "
  "peticiones HTTP con autenticación, encabezados y datos JSON. "
  "El siguiente ejemplo ilustrativo muestra cómo crear una interfaz "
  "Loopback y consultar posteriormente su configuración. "
  "Las credenciales se obtienen de variables de entorno y se "
  "establece un tiempo máximo de espera para cada solicitud. "
  "El parámetro `verify=False` se utiliza únicamente en el "
  "ambiente controlado del laboratorio, ya que deshabilita "
  "la validación del certificado TLS (Reitz, s. f.):")

codigo("""
import os
import requests

USUARIO = os.environ["RESTCONF_USER"]
CLAVE = os.environ["RESTCONF_PASSWORD"]

BASE = "https://10.10.20.48/restconf/data"
URL = BASE + "/ietf-interfaces:interfaces/interface=Loopback501"

H = {"Accept": "application/yang-data+json",
     "Content-Type": "application/yang-data+json"}

cuerpo = {"ietf-interfaces:interface": [{
    "name": "Loopback501",
    "type": "iana-if-type:softwareLoopback",
    "description": "CE5301 - creada por RESTCONF",
    "enabled": True
}]}

# Crear o reemplazar la interfaz
r = requests.put(URL, json=cuerpo, headers=H,
                 auth=(USUARIO, CLAVE),
                 verify=False, timeout=10)
r.raise_for_status()
print(r.status_code)

# Consultar la interfaz
r = requests.get(URL, headers=H,
                 auth=(USUARIO, CLAVE),
                 verify=False, timeout=10)
r.raise_for_status()

datos = r.json()["ietf-interfaces:interface"]
interfaz = datos[0] if isinstance(datos, list) else datos
print(interfaz["description"])
""")

P("La respuesta HTTP 201 indica que se creó un recurso nuevo, "
  "mientras que HTTP 204 indica que se reemplazó uno existente. "
  "La consulta mediante GET permite verificar la configuración "
  "obtenida. En aplicaciones de producción deben utilizarse "
  "certificados confiables y mantenerse habilitada su verificación "
  "(Bierman et al., 2017; Reitz, s. f.).")

P("Los scripts del caso de uso (sección 3.5 y Anexo 1) amplían este ejemplo para recorrer una lista de interfaces, medir el tiempo de cada petición y guardar los resultados.")
H("2.4.5 Herramientas de automatización de la configuración de redes", 3)
P("Las herramientas de gestión de la configuración aplican el estado deseado a muchos equipos a la vez. Se diferencian por quién inicia la comunicación: en el método **push**, el servidor central se conecta a los nodos y les envía la configuración; en el método **pull**, cada nodo tiene un agente que contacta periódicamente al servidor y descarga su configuración. Ansible, por ejemplo, es push por defecto, y su comando `ansible-pull` invierte esa arquitectura para que cada nodo descargue los playbooks desde un repositorio (Red Hat, s. f.). La siguiente tabla compara tres herramientas:")
tabla("Comparación de herramientas de automatización de la configuración.", ["Herramienta", "Método", "Diseño del sistema central", "Sistemas operativos"], [
    ["Ansible", "Push; pull opcional con ansible-pull", "Un nodo de control con el inventario y los playbooks; sin agentes en los nodos, a los que se conecta por SSH, PowerShell remoting o APIs de red", "Nodo de control: Linux, macOS, BSD u otro UNIX con Python (Windows solo con WSL). Nodos: Linux, UNIX, Windows y equipos de red"],
    ["Puppet", "Pull", "Agente y servidor primario: cada agente pide su catálogo al servidor y lo aplica cada 30 minutos por defecto, por HTTPS con certificados; PuppetDB opcional; `puppet apply` sin servidor", "Servidor primario: *nix (Linux). Agentes: *nix, Windows y macOS"],
    ["Salt", "Push y pull", "Master y minions sobre un bus de mensajes ZeroMQ (puertos TCP 4505 y 4506 del master); los minions pueden programar su estado; Salt SSH sin agentes; varios masters o syndic para escalar; proxy minions para equipos de red", "Master: Linux (Debian, Ubuntu, Red Hat, Rocky, etc.) y macOS. Minions: además, Windows"],
], [2.3, 3.2, 5.6, 4.5], 9)
P("Fuentes de la tabla: Red Hat (s. f.), Puppet (s. f.) y Salt Project (s. f.).", 11)
P("**Ansible** no necesita instalar nada en los nodos: el nodo de control ejecuta los módulos y se conecta a cada equipo. Para equipos de red tiene módulos que usan directamente NETCONF y RESTCONF (`netconf_config`, `restconf_get` y `restconf_config` de la colección `ansible.netcommon`), con los que se podría reproducir el caso de uso de este proyecto en un playbook (Red Hat, s. f.).")
P("**Puppet** sigue una arquitectura cliente-servidor: un servidor primario guarda la configuración de los nodos, escrita en el lenguaje declarativo de Puppet; cada agente pide su catálogo individual y lo aplica de forma periódica. La comunicación es por HTTPS con certificados SSL, y PuppetDB puede guardar los datos que generan los agentes (Puppet, s. f.).")
P("**Salt** combina ambos métodos: el master publica trabajos en un bus de mensajes y los minions suscritos los ejecutan (push), pero un minion también puede programar la aplicación de su estado, por ejemplo cada 60 minutos, o trabajar sin master. Salt SSH ejecuta comandos sin instalar el minion, y los proxy minions sirven para equipos de red que no pueden correr un minion propio (Salt Project, s. f.).")
P("Existen otras herramientas con un diseño parecido al de Puppet, como Chef, en la que un servidor central (Chef Infra Server) guarda las políticas y los cookbooks y el cliente de cada nodo aplica las recetas, escritas en Ruby (Progress Chef, s. f.).")

P("**Aplicación al caso de uso.** De las herramientas investigadas, "
  "Ansible representa una alternativa adecuada para ampliar la "
  "solución desarrollada en este proyecto, debido a su arquitectura "
  "sin agentes propios en los dispositivos de red y a la "
  "disponibilidad de módulos compatibles con RESTCONF y NETCONF. "
  "Esto permitiría centralizar el inventario de equipos, reutilizar "
  "configuraciones y aplicar cambios sobre múltiples dispositivos "
  "mediante playbooks. Por su parte, Puppet y Salt ofrecen "
  "mecanismos adicionales de gestión del estado deseado y "
  "automatización mediante agentes intermediarios. Estas "
  "herramientas se investigaron como alternativas y no fueron "
  "evaluadas experimentalmente en el caso de uso "
  "(Red Hat, s. f.; Puppet, s. f.; Salt Project, s. f.).")

salto()
# ---------------------------------------------------------------- CASO DE USO
H("3. Caso de Uso")
H("3.1 Problema seleccionado", 2)
P("Configurar y vigilar interfaces entrando por CLI equipo por equipo es lento, propenso a errores y no avisa cuando algo falla. El caso de uso, aprobado por el profesor el 18 de noviembre de 2026 con tres funcionalidades, automatiza tres tareas de administración sobre un router Cisco IOS XE: configuración, monitoreo y alertas a Webex.")
H("3.2 Solución escogida", 2)
B([
    "**Configuración:** crear, modificar, apagar/encender y borrar interfaces con RESTCONF, desde Postman (PUT, PATCH, DELETE) y desde un script de Python que aplica una lista de interfaces definida en `interfaces.json` (configuración masiva).",
    "**Monitoreo:** consultar `ietf-interfaces:interfaces-state` y comparar el estado administrativo (`admin-status`) y el operativo (`oper-status`) de cada interfaz.",
    "**Alertas a Webex:** si una interfaz está caída, el script envía un mensaje a una sala de Webex mediante la API REST de mensajes, usando un bot creado en developer.webex.com (Webex, s. f.).",
])
H("3.3 Herramientas y requerimientos", 2)
tabla("Herramientas y requerimientos del caso de uso.", ["Componente", "Detalle"], [
    ["Equipo gestionado", "Cisco Catalyst 8000v, IOS XE 17.12.02, sandbox on-demand “Catalyst 8000v” de Cisco DevNet (10.10.20.48)"],
    ["Acceso a la red", "VPN AnyConnect con OpenConnect GUI 1.6.2; red 10.10.20.0/24; puertos 443 (RESTCONF) y 830 (NETCONF)"],
    ["Modelos YANG", "ietf-interfaces (RFC 8343) e ietf-ip (RFC 8344)"],
    ["Cliente", "Postman; Python 3 con requests y ncclient"],
    ["Alertas", "Bot de Webex “CE5301 Alertas RESTCONF” y sala “CE5301 - Alertas de red”"],
    ["Repositorio", "https://github.com/ChrisRC7/Proyecto-de-Redes-de-Computadores, rama main (código, colección Postman y resultados)"],
], [4.0, 11.6])
P("**Nota sobre el sandbox:** los sandboxes compartidos Always On (Catalyst 8000v y 9000v) estaban caídos del lado de Cisco entre el 19 y el 22 de noviembre (reportado por otros usuarios en la Cisco Community), por lo que se reservó el Catalyst 8000v on-demand, privado, con acceso por VPN.")
figura(os.path.join(CAP, "sandbox_cat8kv_ondemand_reserva.jpg"), "Reserva del sandbox Catalyst 8000v on-demand en developer.cisco.com.", 14)
figura(os.path.join(CAP, "vpn_openconnect_conectada.jpg"), "Conexión VPN establecida con OpenConnect hacia el sandbox.", 12)
H("3.4 Arquitectura", 2)
figura(os.path.join(BASE, "figuras", "arquitectura.png"), "Arquitectura del caso de uso: PC, túnel VPN, router Cisco IOS XE y API de Webex.", 15.5)
H("3.5 Implementación", 2)
P("**Colección de Postman** (`CE5301-RESTCONF.postman_collection.json`): usa variables de entorno (`host`, `username`, `password`, `webex_token`, `webex_room_id`) y valida en cada petición un código 2xx y un tiempo de respuesta menor a 5 s.")
tabla("Peticiones de la colección de Postman.", ["#", "Método", "Recurso", "Respuesta esperada"], [
    ["1", "GET", "/restconf", "200"],
    ["2", "GET", "/restconf/data/ietf-interfaces:interfaces", "200"],
    ["3", "PUT", "…/interfaces/interface=Loopback500", "201 / 204"],
    ["4", "GET", "…/interfaces/interface=Loopback500", "200"],
    ["5", "PATCH", "…/interface=Loopback500 (description)", "204"],
    ["6", "GET", "…/interfaces-state/interface=Loopback500", "200"],
    ["7", "PATCH", "…/interface=Loopback500 (enabled=false)", "204"],
    ["8", "GET", "/restconf/data/ietf-interfaces:interfaces-state", "200"],
    ["9", "DELETE", "…/interface=Loopback500", "204"],
    ["10", "POST", "https://webexapis.com/v1/messages", "200"],
], [1.0, 2.0, 9.0, 3.6])
P("**Scripts de Python** (Anexo 1): `configurar_interfaces.py` (acciones crear, listar, modificar, apagar, encender y borrar sobre todas las interfaces de `interfaces.json`), `monitorear_interfaces.py` (consulta el estado, imprime una tabla, guarda un CSV y envía la alerta a Webex), `crear_sala_webex.py` (crea la sala y agrega integrantes) y `netconf_ejemplo.py`. Cada operación registra el código HTTP y el tiempo de respuesta. La configuración y los resultados se pueden repetir para más equipos editando únicamente `interfaces.json`.")
P("**Extracto del monitoreo:** el script lee `interfaces-state`, detecta las interfaces cuyo estado no es `up` y publica el mensaje en Webex:")
codigo("""
r = requests.get(f"{BASE}/ietf-interfaces:interfaces-state", headers=H, auth=AUTH, verify=False)
for i in r.json()["ietf-interfaces:interfaces-state"]["interface"]:
    if i["admin-status"] != "up" or i["oper-status"] != "up":
        caidas.append(i["name"])
if caidas:
    requests.post("https://webexapis.com/v1/messages", headers={"Authorization": f"Bearer {TOKEN}"},
                  json={"roomId": ROOM_ID, "markdown": "**Alerta:** interfaz(es) caída(s): " + ", ".join(caidas)})
""")
H("3.6 Video de la demostración", 2)
VIDEO_URL = "https://youtu.be/JaxwUICyKm4"
_p = P("Enlace al video: ")
_rid = _p.part.relate_to(VIDEO_URL, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink", is_external=True)
_h = OxmlElement("w:hyperlink"); _h.set(qn("r:id"), _rid)
_r = OxmlElement("w:r"); _rpr = OxmlElement("w:rPr")
_f = OxmlElement("w:rFonts")
for _a in ("w:ascii", "w:hAnsi", "w:cs"):
    _f.set(qn(_a), "Arial")
_c = OxmlElement("w:color"); _c.set(qn("w:val"), "0563C1")
_u = OxmlElement("w:u"); _u.set(qn("w:val"), "single")
for _e in (_f, _c, _u):
    _rpr.append(_e)
_t = OxmlElement("w:t"); _t.text = VIDEO_URL
_r.append(_rpr); _r.append(_t); _h.append(_r); _p._p.append(_h)

salto()
# ---------------------------------------------------------------- RESULTADOS
H("4. Resultados y Análisis")
P(f"Las pruebas se ejecutaron el 22 de noviembre de 2026 contra el Catalyst 8000v on-demand, a través de la VPN. Se realizaron tres corridas de crear, listar, modificar y borrar, y una de apagar y encender, con {total_ops} operaciones RESTCONF en total, de las cuales **{total_ok} fueron exitosas ({100*total_ok/total_ops:.0f} %)**. El tiempo de respuesta osciló entre {min(todos_t):.0f} ms y {max(todos_t):.0f} ms, con una media de {statistics.mean(todos_t):.0f} ms.")
tabla("Resultados de las operaciones de configuración (tres interfaces por corrida).", ["Acción", "HTTP esperado", "Operaciones", "Exitosas", "Mín. (ms)", "Media (ms)", "Máx. (ms)"], filas_cfg, [2.4, 3.0, 2.4, 2.0, 1.8, 2.0, 2.0], 9)
P("Las lecturas (GET) fueron las más rápidas (media cercana a 300 ms); las modificaciones con PATCH y la creación con PUT estuvieron entre 0,9 y 1,2 s, y el borrado (DELETE) fue la operación más lenta (media cercana a 2,3 s), pues el router debe aplicar el cambio de configuración. Los códigos HTTP fueron los que define el RFC 8040: 201 al crear un recurso nuevo, 200 al leer y 204 cuando la operación se realizó sin contenido de respuesta (Bierman et al., 2017).")
tabla("Resultados del monitoreo de interfaces.", ["Fecha y hora", "Interfaces leídas", "Consulta de estado (ms)", "Consulta de configuración (ms)", "Interfaces caídas"], filas_mon, [3.6, 2.4, 3.0, 3.4, 3.2], 9)
P("En la primera consulta el tiempo fue de 4 231 ms, mayor que el resto, que estuvo alrededor de 1 segundo (937 ms a 1 372 ms). Esto se atribuye al establecimiento de la conexión HTTPS y al primer acceso a los datos operativos tras abrir el túnel. El monitoreo detectó correctamente la caída de la Loopback502 apagada a propósito y, en la corrida sobre todo el router, reportó como no activas GigabitEthernet2 y GigabitEthernet3, que están administrativamente apagadas (shutdown) en el router.")
P("**Validación de la alerta:** al apagar la Loopback502 con PATCH (`enabled=false`), el monitoreo la identificó como caída y el envío a la API de Webex devolvió HTTP 200; el mensaje apareció en la sala “CE5301 - Alertas de red” (Figuras #12 y #15). Al volver a encenderla y borrarla, el router quedó en su estado inicial.")
P("**NETCONF:** la sesión SSH al puerto 830 se abrió en 2 764 ms y el `get-config` respondió en 389 ms. La apertura de la sesión es más lenta que una petición RESTCONF porque implica el intercambio de claves SSH y de `<hello>`; luego las operaciones son rápidas.")
P("**Capturas de cada paso** (entrada y salida de los scripts):")
pasos = [("01_conectividad.png", "Verificación de conectividad RESTCONF (GET, HTTP 200)."),
         ("02_crear.png", "Creación de Loopback501 a 503 con PUT (HTTP 201)."),
         ("03_listar.png", "Consulta de las interfaces creadas con GET (HTTP 200)."),
         ("04_modificar.png", "Cambio de descripción con PATCH (HTTP 204)."),
         ("05_monitorear.png", "Monitoreo con las tres interfaces activas."),
         ("06_apagar.png", "Apagado de Loopback502 con PATCH (HTTP 204)."),
         ("07_alerta.png", "Detección de la interfaz caída y envío de la alerta a Webex."),
         ("08_encender.png", "Encendido de Loopback502 con PATCH (HTTP 204)."),
         ("09_borrar.png", "Borrado de las interfaces con DELETE (HTTP 204).")]
for f, d in pasos:
    figura(os.path.join(TER, f), d, 15.0)
figura(os.path.join(CAP, "webex_alerta_interfaz_caida.jpg"), "Mensaje de alerta recibido en la sala de Webex.", 13)
P("**Colección de Postman:** el 23 de noviembre de 2026 se ejecutó la colección completa con Newman, el ejecutor de línea de comandos de Postman, contra el mismo router y por la VPN. Se ejecutaron 10 peticiones y 20 aserciones, **sin ningún fallo**, en 8.4 s en total, con un tiempo de respuesta medio de 760 ms (mínimo 157 ms y máximo 2 087 ms). El reporte completo está en `caso-de-uso/resultados/postman/`.")
figura(os.path.join(BASE, "..", "caso-de-uso", "capturas", "postman", "newman_reporte.png"), "Reporte de la ejecución de la colección de Postman con Newman.", 14)
tabla("Resultados de la ejecución de la colección de Postman (Newman).", ["#", "Petición", "HTTP", "Tiempo (ms)"], [
    ["1", "GET capacidades RESTCONF", "200", "595"],
    ["2", "GET todas las interfaces (configuración)", "200", "247"],
    ["3", "PUT crear Loopback", "201", "660"],
    ["4", "GET Loopback (verificar creación)", "200", "157"],
    ["5", "PATCH modificar descripción", "204", "783"],
    ["6", "GET estado operativo de la Loopback", "200", "196"],
    ["7", "PATCH apagar Loopback", "204", "404"],
    ["8", "GET estado de todas las interfaces", "200", "1 388"],
    ["9", "DELETE borrar Loopback", "204", "2 087"],
    ["10", "POST alerta a Webex", "200", "1 085"],
], [1.0, 8.6, 2.4, 3.6])
P("**Análisis:** se logró la comunicación entre la PC y el router y el funcionamiento buscado en las tres funcionalidades, con 100 % de éxito en las operaciones medidas. Como limitaciones: la medición proviene de un sandbox compartido y accedido por VPN, por lo que los tiempos incluyen la latencia del túnel; las pruebas se hicieron con tres interfaces loopback; y la colección de Postman se ejecutó con Newman (línea de comandos), no con la interfaz gráfica de Postman.")

# ---------------------------------------------------------------- CONCLUSIONES
H("5. Conclusiones y Recomendaciones")
H("5.1 Conclusiones", 2)
B([
    "RESTCONF con los modelos YANG estándar permitió crear, modificar, consultar y borrar interfaces de un router IOS XE sin usar la CLI, con 100 % de operaciones exitosas en las pruebas.",
    "El monitoreo mediante `interfaces-state` detectó las interfaces caídas, y la integración con la API de Webex entregó la alerta en la sala de Webex.",
    "NETCONF y RESTCONF exponen los mismos modelos YANG; RESTCONF resultó más sencillo de usar con Postman y Python, mientras que NETCONF ofrece sesiones con estado y transacciones.",
    "**Christopher.** Como responsable de la parte técnica, la principal dificultad no fue el código sino la infraestructura: los sandboxes Always On no estaban disponibles y hubo que pasar a un Catalyst 8000v on-demand por VPN, con una reserva que vence y debe renovarse. Una vez resuelto, el mismo script sirvió para crear, modificar, consultar y borrar interfaces, y para enviar la alerta a Webex con 100 % de éxito en las operaciones medidas. La colección de Postman también se ejecutó completa, con 10 peticiones y 20 aserciones sin fallos.",
    "**Javier.** El desarrollo de este desafío me permitió "
    "comprender cómo la programabilidad basada en modelos facilita "
    "la administración de redes, especialmente mediante RESTCONF "
    "y YANG. La utilización de herramientas como Postman y Python "
    "demuestra que es posible automatizar tareas que tradicionalmente "
    "se realizan de forma manual, reduciendo la intervención del "
    "administrador y facilitando la configuración de múltiples "
    "interfaces. Asimismo, la integración con Webex permitió "
    "evidenciar la utilidad de combinar diferentes APIs para detectar "
    "y comunicar problemas en la red. Considero que una mejora "
    "importante sería implementar un monitoreo continuo y distinguir "
    "entre las interfaces deshabilitadas intencionalmente y aquellas "
    "que presentan una falla real, evitando así generar alertas "
    "innecesarias.",
])
H("5.2 Recomendaciones y mejoras", 2)
B([
    "Ejecutar el monitoreo de forma continua (el script admite un intervalo) y usar notificaciones de NETCONF o telemetría para evitar el sondeo.",
    "Usar certificados válidos y guardar las credenciales y el token del bot en variables de entorno o un gestor de secretos, y no en el código.",
    "Reemplazar `interfaces-state` por los datos operativos del modelo NMDA, pues el RFC 8343 lo marca como obsoleto (Bjørklund, 2018a).",
    "Ampliar el inventario a más dispositivos y fabricantes y agregar reintentos ante fallos de red.",
    "Reservar el sandbox con anticipación y verificar su estado, pues los sandboxes Always On pueden dejar de estar disponibles.",
])

# ---------------------------------------------------------------- REFERENCIAS
salto()
H("6. Referencias Bibliográficas")
refs = [
 "Amazon Web Services. (s. f.). ¿Qué es DevOps? https://aws.amazon.com/es/devops/what-is-devops/",
 "Bierman, A., Bjørklund, M., & Watsen, K. (2017). RESTCONF Protocol (RFC 8040). Internet Engineering Task Force. https://www.rfc-editor.org/info/rfc8040",
 "Bjørklund, M. (s. f.). pyang [Software]. GitHub. https://github.com/mbj4668/pyang",
 "Bjørklund, M. (2010). YANG - A Data Modeling Language for the Network Configuration Protocol (NETCONF) (RFC 6020). Internet Engineering Task Force. https://www.rfc-editor.org/info/rfc6020",
 "Bjørklund, M. (2016). The YANG 1.1 Data Modeling Language (RFC 7950). Internet Engineering Task Force. https://www.rfc-editor.org/info/rfc7950",
 "Bjørklund, M. (2018a). A YANG Data Model for Interface Management (RFC 8343). Internet Engineering Task Force. https://www.rfc-editor.org/info/rfc8343",
 "Bjørklund, M. (2018b). A YANG Data Model for IP Management (RFC 8344). Internet Engineering Task Force. https://www.rfc-editor.org/info/rfc8344",
 "Bjørklund, M., & Berger, L. (2018). YANG Tree Diagrams (RFC 8340). Internet Engineering Task Force. https://www.rfc-editor.org/info/rfc8340",
 "Case, J., Fedor, M., Schoffstall, M., & Davin, J. (1990). A Simple Network Management Protocol (SNMP) (RFC 1157). Internet Engineering Task Force. https://www.rfc-editor.org/info/rfc1157",
 "Cisco Systems. (s. f.-a). DevNet: Network automation and DevOps. Cisco DevNet. https://developer.cisco.com/",
 "Cisco Systems. (s. f.-b). Programmability Configuration Guide, Cisco IOS XE Dublin 17.12.x. Cisco. https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/prog/configuration/1712/b_1712_programmability_cg.html",
 "Enns, R., Bjørklund, M., Schönwälder, J., & Bierman, A. (2011). Network Configuration Protocol (NETCONF) (RFC 6241). Internet Engineering Task Force. https://www.rfc-editor.org/info/rfc6241",
 "Lhotka, L. (2016). JSON Encoding of Data Modeled with YANG (RFC 7951). Internet Engineering Task Force. https://www.rfc-editor.org/info/rfc7951",
 "Postman. (s. f.). Postman Learning Center. https://learning.postman.com/docs/",
 "Pras, A., & Schönwälder, J. (2003). On the Difference between Information Models and Data Models (RFC 3444). Internet Engineering Task Force. https://www.rfc-editor.org/info/rfc3444",
 "Progress Chef. (s. f.). Chef Infra documentation. https://docs.chef.io/",
 "Puppet. (s. f.). Puppet Core documentation. https://help.puppet.com/core/current/Content/PuppetCore/puppet_index.htm",
 "Red Hat. (s. f.). Ansible documentation. https://docs.ansible.com/",
 "Reitz, K. (s. f.). Requests: HTTP for Humans. https://requests.readthedocs.io/",
 "Salt Project. (s. f.). Salt documentation. https://docs.saltproject.io/",
 "Schönwälder, J. (2003). Overview of the 2002 IAB Network Management Workshop (RFC 3535). Internet Engineering Task Force. https://www.rfc-editor.org/info/rfc3535",
 "Shafer, P. (2011). An Architecture for Network Management Using NETCONF and YANG (RFC 6244). Internet Engineering Task Force. https://www.rfc-editor.org/info/rfc6244",
 "Wasserman, M. (2011). Using the NETCONF Protocol over Secure Shell (SSH) (RFC 6242). Internet Engineering Task Force. https://www.rfc-editor.org/info/rfc6242",
 "Webex. (s. f.). Webex for Developers: Messages API. Cisco. https://developer.webex.com/messaging/docs/api/v1/messages",
 "Bjørklund, M., Schönwälder, J., Shafer, P., Watsen, K., & Wilton, R. (2019). RESTCONF Extensions to Support the Network Management Datastore Architecture (RFC 8527). Internet Engineering Task Force. https://www.rfc-editor.org/info/rfc8527",
]
for r_ in refs:
    p = doc.add_paragraph(); p.alignment = J
    p.paragraph_format.left_indent = Cm(1.0); p.paragraph_format.first_line_indent = Cm(-1.0)
    runs(p, r_)

# ---------------------------------------------------------------- ANEXO 1
salto()
H("Anexo 1: Configuraciones o Código Fuente")
P("El código completo se encuentra en el repositorio del proyecto, https://github.com/ChrisRC7/Proyecto-de-Redes-de-Computadores, rama `main`, carpeta `caso-de-uso/`. [[PENDIENTE (Christopher): dar acceso al profesor o hacer público el repositorio, que hoy es privado.]] Contenido:")
tabla("Archivos del Anexo 1.", ["Archivo", "Descripción"], [
    ["configurar_interfaces.py", "Crear, listar, modificar, apagar, encender y borrar interfaces vía RESTCONF"],
    ["monitorear_interfaces.py", "Monitoreo de estado y alerta a Webex"],
    ["crear_sala_webex.py", "Creación de la sala de alertas y adición de miembros"],
    ["netconf_ejemplo.py", "Ejemplo NETCONF get-config con ncclient"],
    ["config.py, interfaces.json, .env.example, requirements.txt", "Configuración, lista de interfaces y dependencias"],
    ["postman/*.json", "Colección y entorno de Postman"],
    ["yang/", "Árboles YANG generados con pyang"],
    ["resultados/", "CSV y logs de las pruebas"],
], [6.0, 9.6])
for nombre in ["configurar_interfaces.py", "monitorear_interfaces.py"]:
    P(f"**{nombre}**")
    with open(os.path.join(CASO, nombre), encoding="utf-8") as fh:
        codigo(fh.read())

# ---------------------------------------------------------------- ANEXO 2
salto()
H("Anexo 2: Trabajo individual y en equipo")
H("A2.1 Metas del proyecto", 2)
tabla("Metas y entregables del proyecto.", ["Meta", "Entregable asociado"], [
    ["Investigar la programabilidad basada en modelos, YANG, NETCONF, RESTCONF y herramientas de automatización", "Sección de Investigación del informe"],
    ["Implementar un caso de uso de configuración, monitoreo y alertas con RESTCONF", "Scripts de Python, colección de Postman y resultados (Anexo 1)"],
    ["Demostrar el caso de uso en un video de máximo 10 minutos", "Video con participación de los tres integrantes"],
    ["Documentar el proyecto", "Informe en PDF y Anexo 2"],
], [8.0, 7.6])
H("A2.2 Roles y responsabilidades", 2)
tabla("Roles del equipo.", ["Integrante", "Rol", "Responsabilidades principales"], [
    ["Christopher", "Coordinador y líder técnico", "Caso de uso (Postman y Python), sandbox, Anexo 1, investigación del bloque NETCONF y convocatoria de reuniones"],
    ["Randall", "Líder de investigación y editor del informe", "Investigación de programabilidad y YANG, integración y formato del informe, referencias APA"],
    ["Javier", "Líder de documentación y video", "Investigación de RESTCONF y herramientas, Anexo 2 (minutas y cronograma), guion y edición del video"],
], [2.6, 4.4, 8.6])
H("A2.3 Reglas del equipo", 2)
B([
    "Comunicación: las reuniones del equipo son por llamada de voz y video de Discord, en el canal “Proyecto Redes”; Christopher las convoca.",
    "Cada reunión deja una minuta con fecha, asistentes, agenda, acuerdos y tareas con responsable y fecha límite, además de una captura como evidencia; Javier coordina las minutas y la redacción rota entre Javier, Randall y Christopher.",
    "Plazos: toda tarea tiene un responsable y una fecha límite fijada en la minuta; el trabajo se termina con anticipación para dejar tiempo de revisión antes de la entrega del 26 de nov.",
    "Código: se trabaja en un repositorio de Git con commits descriptivos; Christopher es responsable del merge a main.",
    "Revisión cruzada: cada pieza la revisa una persona distinta de quien la hizo (Randall prueba los scripts con el README; Christopher revisa el PDF contra la rúbrica).",
    "Investigación: cada dato lleva su cita y no se usa Wikipedia.",
    "Bitácora y evaluación: cada integrante lleva su bitácora y llena el formulario de evaluación individual y coevaluación.",
])
H("A2.4 Cronograma", 2)
tabla("Cronograma de actividades.", ["Fase", "Actividad", "Responsable", "Fechas"], [
    ["0", "Arranque: caso de uso, roles, carpeta y repositorio", "Todos", "12 a 14 nov"],
    ["1", "Investigación (bloques A, B, C y D)", "Randall (A, B), Christopher (C), Javier (D)", "14 a 18 nov"],
    ["2", "Caso de uso: scripts, colección Postman y alertas Webex", "Christopher", "15 a 22 nov"],
    ["3", "Informe", "Randall (edición), todos", "18 a 23 nov"],
    ["4", "Video", "Javier (edición), todos", "21 a 24 nov"],
    ["5", "Cierre, PDF y entrega en TEC Digital", "Randall, Christopher, Javier", "24 a 26 nov"],
], [1.2, 6.8, 4.6, 3.0])
H("A2.5 Minutas", 2)
H("Minuta 1: Reunión de arranque y definición del caso de uso", 3)
tabla("Datos de la Minuta 1.", ["Campo", "Detalle"], [
    ["Fecha", "18 de noviembre de 2026"],
    ["Hora y duración", "La captura muestra el reloj en 10:24 y la llamada en 32:28, por lo que la reunión comenzó cerca de las 9:51 y duró al menos 32 minutos."],
    ["Medio", "Llamada de voz y video por Discord, canal “Proyecto Redes”"],
    ["Asistentes", "Christopher Rodríguez, Javier Tenorio y Randall Bolaños"],
    ["Redactor", "Javier"],
    ["Evidencia", "Figura siguiente (captura de Discord del 18 de noviembre)"],
], [4.0, 11.6])
P("[[PENDIENTE: adjuntar aquí la captura real de esta reunión; la imagen anterior fue retirada.]]")
P("**Agenda:** lectura del enunciado y de la rúbrica del Desafío de Redes (CE-5301); elección del caso de uso; definición de roles y reglas del equipo; cronograma y fechas de reuniones.")
P("**Desarrollo:**")
B([
    "Se revisó el enunciado: informe en PDF, video de máximo 10 minutos con todos en cámara, y Anexo 2 con al menos tres minutas y tres bitácoras.",
    "Se propuso como caso de uso la configuración y el monitoreo de interfaces de un router Cisco IOS XE por RESTCONF, sobre el modelo YANG ietf-interfaces, con Postman y scripts de Python (requests). Se eligió porque reemplaza la configuración por CLI equipo por equipo y cubre las áreas de configuración y monitoreo del enunciado.",
    "Se consultó al profesor si bastaba ese alcance. Respondió que el caso de uso estaba aprobado, pero que debía tener al menos tres funcionalidades; se acordó cubrir configuración, monitoreo y una tercera de alertas a Webex, que el profesor también aprobó.",
    "Se propuso el sandbox gratuito “IOS XE on Cat8kv Always-On” de developer.cisco.com.",
    "Se repartió la investigación: bloques A y B para Randall, bloque C (NETCONF) para Christopher y bloque D (RESTCONF y herramientas de automatización) para Javier.",
])
tabla("Acuerdos de la Minuta 1.", ["#", "Acuerdo"], [
    ["1", "Se adopta el caso de uso RESTCONF sobre ietf-interfaces, aprobado por el profesor, con tres funcionalidades: configuración, monitoreo y alerta a Webex."],
    ["2", "Roles: Christopher, coordinador y líder técnico; Randall, líder de investigación y editor del informe; Javier, documentación del equipo y video."],
    ["3", "Reglas del equipo: las descritas en la sección A2.3."],
    ["4", "Reuniones mínimas: 20 nov (avance de investigación y demo preliminar) y 23 nov (revisión de informe y video)."],
    ["5", "Cada integrante lleva su bitácora personal."],
], [1.2, 14.4])
tabla("Tareas asignadas en la Minuta 1.", ["Tarea", "Responsable", "Fecha límite"], [
    ["Crear cuenta en developer.cisco.com y reservar el sandbox", "Christopher", "20 nov"],
    ["Instalar Postman y Python (requests, ncclient, pyang)", "Christopher", "20 nov"],
    ["Carpeta compartida y repositorio de código", "Christopher", "20 nov"],
    ["Plantilla del informe (Arial 12, justificado)", "Randall", "20 nov"],
    ["Investigación bloques A y B", "Randall", "20 nov"],
    ["Plantillas de minuta y bitácora; borrador de metas, roles y cronograma", "Javier", "20 nov"],
    ["Investigación bloque D", "Javier", "20 nov"],
    ["Investigación bloque C", "Christopher", "20 nov"],
], [9.0, 3.4, 3.2])
P("Próxima reunión: 20 de noviembre, avance de investigación y demo preliminar.")

H("Minuta 2: Avance de investigación y demo preliminar", 3)
tabla("Datos de la Minuta 2.", ["Campo", "Detalle"], [
    ["Fecha", "20 de noviembre de 2026"],
    ["Hora y duración", "La captura muestra el reloj en 07:07 y la llamada en 28:37, por lo que la reunión comenzó cerca de las 6:38 y duró al menos 28 minutos."],
    ["Medio", "Llamada de voz y video por Discord, canal “Proyecto Redes”"],
    ["Asistentes", "Christopher Rodríguez, Javier Tenorio y Randall Bolaños"],
    ["Redactor", "Randall"],
    ["Evidencia", "Figura siguiente (captura de Discord del 20 de noviembre)"],
], [4.0, 11.6])
P("[[PENDIENTE: adjuntar aquí la captura real de esta reunión; la imagen anterior fue retirada.]]")
P("**Agenda:** seguimiento de las tareas de la Minuta 1; estado de la investigación por bloque; avance del caso de uso (scripts, colección de Postman y alertas a Webex); problemas y riesgos; ajustes al cronograma.")
P("**Desarrollo:**")
B([
    "Seguimiento: se confirmó el alcance de tres funcionalidades aprobado por el profesor (configuración, monitoreo y alerta a Webex).",
    "Investigación: Randall presentó los bloques A y B (programabilidad basada en modelos y YANG), Christopher el bloque C (NETCONF) y Javier el bloque D (RESTCONF y herramientas de automatización); Randall quedó a cargo de integrarlos en un solo documento.",
    "Avance del caso de uso: Christopher reportó los scripts de RESTCONF, la colección de Postman y el ejemplo de NETCONF en el repositorio, y el bot de Webex con la sala de alertas, probada con un mensaje de prueba. Faltaba probar todo contra un router.",
    "Riesgo: los sandboxes Always On de Cisco presentaban fallas y se debía conseguir un router alterno para probar los scripts.",
])
tabla("Acuerdos de la Minuta 2.", ["#", "Acuerdo"], [
    ["1", "Queda confirmado el alcance de tres funcionalidades (configuración, monitoreo y alerta a Webex)."],
    ["2", "Las alertas se envían con un bot de Webex a una sala del equipo."],
    ["3", "Christopher busca un router alterno si el sandbox Always On sigue sin responder."],
    ["4", "Randall integra los bloques de investigación en un solo documento con estilo uniforme."],
], [1.2, 14.4])
tabla("Tareas asignadas en la Minuta 2.", ["Tarea", "Responsable", "Fecha límite"], [
    ["Probar la colección Postman (GET, PUT, PATCH, DELETE) y los scripts contra un router", "Christopher", "22 nov"],
    ["Resolver el acceso al sandbox y reservarlo", "Christopher", "22 nov"],
    ["Crear el bot y la sala en developer.webex.com", "Christopher", "20 nov"],
    ["Diagrama de arquitectura (PC, VPN, router, flujo REST)", "Javier", "22 nov"],
    ["Guion del video con tiempos (meta 9 min)", "Javier", "21 nov"],
    ["Integrar y dar formato al informe; referencias APA", "Randall", "22 nov"],
    ["Probar los scripts siguiendo el README (validación independiente)", "Randall", "23 nov"],
], [9.0, 3.4, 3.2])
P("Próxima reunión: 23 de noviembre, revisión de informe y video.")

H("Minuta 3: Revisión de informe y video", 3)
tabla("Datos de la Minuta 3.", ["Campo", "Detalle"], [
    ["Fecha", "23 de noviembre de 2026"],
    ["Hora y duración", "La captura se tomó a las 6:12 p. m. con la llamada en 24:52, por lo que la reunión comenzó cerca de las 5:47 p. m. y duró al menos 25 minutos."],
    ["Medio", "Llamada de voz y video por Discord, canal “Proyecto Redes”"],
    ["Asistentes", "Christopher Rodríguez, Javier Tenorio y Randall Bolaños"],
    ["Redactor", "Christopher"],
    ["Evidencia", "Figura siguiente (captura de Discord del 23 de noviembre)"],
], [4.0, 11.6])
figura(os.path.join(BASE, "..", "Capturas", "WhatsApp Image 2026-11-23 at 6.12.33 PM.jpeg"), "Captura de la reunión del 23 de noviembre de 2026 en Discord.", 14)
P("**Agenda:** estado del informe (36 páginas en borrador) y marcadores pendientes; resultados del caso de uso y datos cuantitativos; guion, reparto y grabación del video; Anexo 2; plan hasta la entrega del 26 de noviembre.")
P("**Desarrollo:**")
B([
    "Resultados del caso de uso (probados el 22 nov): crear con PUT 201, listar con GET 200, modificar y apagar o encender con PATCH 204, borrar con DELETE 204, con 100 % de éxito. El GET RESTCONF respondió HTTP 200 en unos 0,7 s por VPN y el NETCONF get-config en 389 ms. El monitoreo detectó la Loopback502 apagada y envió la alerta a Webex (HTTP 200).",
    "Sandbox: los sandboxes Always On (Cat8000v y Cat9000v) siguieron caídos del lado de Cisco, por lo que se usó el Catalyst 8000v on-demand (privado, IOS XE 17.12.02), reservado el 22 de nov, por VPN con OpenConnect. La reserva dura 48 horas y hay que renovarla antes de grabar el video.",
    "Pendiente técnico: correr la colección de Postman con la VPN activa y capturarla antes de que venza la reserva (24 nov, 13:22).",
    "Video: Randall introduce (0:00 a 2:00), Javier presenta arquitectura y requerimientos (2:00 a 4:00), Christopher hace la demostración (4:00 a 8:30) y Randall o Javier cierran (8:30 a 9:00). Todos con cámara; máximo 10 minutos, meta 9. Existen el guion, seis diapositivas básicas y una grabación de respaldo de la demo sin audio (2:45).",
    "Informe: faltan las reglas del equipo, las reflexiones del Anexo 2, los párrafos de conclusión de Randall y Javier, la verificación de URLs y fechas de las referencias, el enlace del video y el enlace de GitHub tras el merge a main.",
    "Anexo 2: las tres minutas quedaron con su captura de Discord (18, 20 y 23 de nov), con metas, roles, reglas y cronograma. Faltan que Randall y Javier completen las duraciones de su bitácora y la reflexión grupal sobre eficiencia.",
])
tabla("Acuerdos de la Minuta 3.", ["#", "Acuerdo"], [
    ["1", "Se usa el sandbox on-demand por VPN en lugar del Always On y se renueva la reserva antes de grabar el video."],
    ["2", "Cada integrante graba su parte con cámara y cronometra un ensayo."],
    ["3", "Christopher hace el merge a main y entrega el enlace del repositorio."],
    ["4", "Revisión visual del PDF página por página (justificado, pies de figura en Arial 11)."],
    ["5", "Cada quien completa su bitácora y el formulario de evaluación individual y coevaluación."],
], [1.2, 14.4])
tabla("Tareas asignadas en la Minuta 3.", ["Tarea", "Responsable", "Fecha límite"], [
    ["Correr la colección Postman con VPN activa y capturar", "Christopher", "24 nov"],
    ["Merge a main y enlace de GitHub en el Anexo 1", "Christopher", "24 nov"],
    ["Grabar la demostración con voz y cámara", "Christopher", "24 nov"],
    ["Grabar la introducción y el cierre", "Randall", "24 nov"],
    ["Insertar el enlace del video (sección 3.6) y exportar el PDF final", "Randall", "25 nov"],
    ["Grabar arquitectura y requerimientos; editar y unir el video (máx. 10:00)", "Javier", "25 nov"],
    ["Verificar el enlace del video desde otra cuenta", "Javier", "25 nov"],
    ["Anexo 2 completo: reglas, minutas, bitácoras y reflexión", "Javier y todos", "25 nov"],
    ["Revisión cruzada del PDF contra la rúbrica", "Christopher", "25 nov"],
    ["Subir una sola copia a TEC Digital", "Christopher", "26 nov"],
], [9.0, 3.4, 3.2])
P("Próxima reunión (opcional): 25 de noviembre, cierre y lecciones aprendidas.")
H("A2.6 Bitácoras individuales", 2)
P("**Christopher.** Entradas reconstruidas a partir del historial del repositorio, las capturas y las minutas; las duraciones sin dato deben completarse.")
tabla("Bitácora de Christopher.", ["Fecha", "Actividad", "Duración"], [
    ["12 nov", "Creación del repositorio y primeras tareas", "45 min aprox."],
    ["18 nov", "Reunión 1 por Discord (Minuta 1): caso de uso aprobado y reparto de tareas", "Más de 32 min"],
    ["20 nov", "Reunión 2 por Discord (Minuta 2): avance de investigación y del caso de uso", "Más de 28 min"],
    ["20 nov", "Scripts RESTCONF, colección Postman, ejemplo NETCONF; bot y sala de Webex; captura del mensaje de prueba", "4 h 30 min aprox."],
    ["22 nov", "Diagnóstico de la falla de los sandboxes Always On; reserva del Cat8000v on-demand; pruebas del caso de uso (RESTCONF, NETCONF, alerta a Webex); árboles YANG con pyang; capturas, guion de la demo y grabación de respaldo; subida al repositorio", "6 h aprox."],
    ["23 nov", "Reunión 3 por Discord (Minuta 3): revisión de informe y video", "Más de 24 min"],
], [2.2, 10.4, 3.0])


P("**Javier.** Registro de las actividades realizadas en la "
  "investigación de RESTCONF, la documentación del caso de uso, "
  "la organización del trabajo en equipo y la preparación del video.")

tabla("Bitácora de Javier.", ["Fecha", "Actividad", "Duración"], [
    ["18 nov", "Participación en la reunión 1 por Discord (Minuta 1): "
     "definición del caso de uso, distribución de responsabilidades "
     "y planificación del proyecto.", "Más de 32 min"],

    ["18-20 nov", "Investigación sobre Postman, solicitudes RESTCONF "
     "con Python y herramientas de automatización Ansible, Puppet "
     "y Salt.", "2 h 30 min aprox."],

    ["20 nov", "Participación en la reunión 2 por Discord (Minuta 2): "
     "revisión del avance de la investigación y del caso de uso.",
     "Más de 28 min"],

    ["20-23 nov", "Documentación del problema seleccionado, "
     "la solución propuesta y las herramientas utilizadas "
     "en el caso de uso.", "1 h 30 min aprox."],

    ["20-23 nov", "Elaboración del diagrama de arquitectura del "
     "sistema, considerando la conexión VPN, el router Cisco "
     "y la integración con Webex.", "1 h aprox."],

    ["23 nov", "Participación en la reunión 3 por Discord (Minuta 3): "
     "revisión de resultados, informe, distribución del video "
     "y actividades pendientes.", "Más de 24 min"],

    ["21-24 nov", "Preparación del guion, distribución de tiempos "
     "y diapositivas de apoyo para el video.", "2 h 30 min aprox."],

    ["24-25 nov", "Revisión y organización del Anexo 2: metas, "
     "roles, reglas, cronograma y minutas del equipo.", "2 h aprox."],

    ["25 nov", "Redacción de la reflexión grupal sobre eficiencia, "
     "equidad, inclusión y colaboración (TE5-TE7) y redacción "
     "de la conclusión personal.", "1 h aprox."],
], [2.2, 10.4, 3.0])


P("**Randall.** Registro de las actividades realizadas como líder "
  "de investigación y editor del informe, incluyendo la investigación "
  "sobre programabilidad basada en modelos y YANG, la integración "
  "de los contenidos, la revisión bibliográfica y el formato del documento.")

tabla("Bitácora de Randall.", ["Fecha", "Actividad", "Duración"], [
    ["12-18 nov", "Preparación de la plantilla del informe según "
     "los requerimientos de formato establecidos por el profesor.",
     "1 h aprox."],

    ["18 nov", "Participación en la reunión 1 por Discord (Minuta 1): "
     "definición del caso de uso, distribución de responsabilidades "
     "y planificación del proyecto.", "Más de 32 min"],

    ["14-20 nov", "Investigación sobre programabilidad basada en modelos, "
     "DevOps, SNMP, RFC 3535, bloques básicos de construcción "
     "y modelos de datos.", "2 h aprox."],

    ["14-20 nov", "Investigación sobre el lenguaje YANG, estructura "
     "de los modelos de datos, YANG data y utilización de pyang "
     "para explorar modelos.", "2 h aprox."],

    ["20 nov", "Participación en la reunión 2 por Discord (Minuta 2): "
     "presentación de los bloques de investigación A y B y revisión "
     "del avance del caso de uso.", "Más de 28 min"],

    ["20 nov", "Redacción y organización de la Minuta 2, incluyendo "
     "los acuerdos, actividades pendientes y responsables.",
     "30 min aprox."],

    ["20-24 nov", "Integración de los cuatro bloques de investigación "
     "en el informe y unificación de la redacción y el estilo "
     "del documento.", "1 h 30 min aprox."],

    ["23 nov", "Participación en la reunión 3 por Discord (Minuta 3): "
     "revisión de resultados, estado del informe, distribución "
     "del video y actividades pendientes.", "Más de 24 min"],

    ["24 nov", "Organización y revisión de las referencias bibliográficas "
     "en formato APA, verificación de los enlaces y correspondencia "
     "entre las citas y las referencias del informe.",
     "1 h 30 min aprox."],

], [2.2, 10.4, 3.0])

H("A2.7 Evaluación de la eficiencia", 2)

P("**Eficiencia y efectividad del trabajo (TE5).** "
  "La organización del proyecto permitió distribuir las actividades "
  "entre los tres integrantes y avanzar de forma paralela en la "
  "investigación, la implementación técnica y la documentación. "
  "En la parte práctica se consiguió configurar y monitorear interfaces "
  "mediante RESTCONF, así como enviar alertas automáticas a Webex. "
  "Las pruebas registraron un 100 % de operaciones exitosas en los "
  "escenarios evaluados. Sin embargo, se identificaron dificultades "
  "con la disponibilidad de los sandboxes de Cisco, lo que obligó "
  "a cambiar a un entorno on-demand y ajustar el cronograma.")

P("**Equidad e inclusión en la distribución del trabajo (TE6).** "
  "Las responsabilidades se distribuyeron según las funciones "
  "acordadas por el grupo. Christopher se encargó principalmente "
  "de la implementación técnica y NETCONF; Randall desarrolló "
  "la investigación de programabilidad y YANG, además de integrar "
  "el informe; y Javier asumió la investigación de RESTCONF, "
  "la documentación del trabajo en equipo y la preparación del video. "
  "La distribución permitió que cada integrante contribuyera "
  "con investigación, documentación y exposición. Como mejora, "
  "convendría revisar periódicamente la carga de trabajo para "
  "redistribuir tareas cuando alguna actividad requiera más "
  "tiempo del previsto.")

P("**Colaboración y cooperación (TE7).** "
  "Las reuniones de seguimiento permitieron revisar el progreso, "
  "discutir dificultades y asignar responsabilidades con fechas "
  "de cumplimiento. El equipo compartió los avances mediante "
  "el repositorio y las minutas de trabajo. Un ejemplo de "
  "colaboración fue la adaptación del caso de uso cuando "
  "los sandboxes Always On no estuvieron disponibles, "
  "lo que permitió continuar las pruebas con un entorno "
  "alternativo. Se considera importante mantener estas "
  "prácticas y reforzar la validación cruzada de los entregables.")

P("**Oportunidades de mejora.** "
  "Para futuros proyectos se recomienda registrar las actividades "
  "y su duración desde el momento en que se realizan, conservar "
  "las evidencias de cada reunión, anticipar alternativas ante "
  "fallas de infraestructura externa y reservar tiempo suficiente "
  "para integrar y revisar los entregables finales.")

P("**Evaluación individual y coevaluación.** "
  "De acuerdo con las indicaciones del desafío, cada integrante "
  "debe completar de forma individual el formulario de "
  "autoevaluación y coevaluación del equipo. Esta reflexión "
  "grupal complementa dicho proceso, pero no sustituye "
  "las evaluaciones individuales obligatorias.")

doc.save(os.path.join(BASE, "Informe.docx"))
print("Informe.docx generado")
