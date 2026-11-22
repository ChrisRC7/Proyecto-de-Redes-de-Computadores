# Árboles YANG (pyang)

Salida de `pyang -f tree` para los modelos que usa el caso de uso (para el Bloque B del informe).

```powershell
pyang -f tree ietf-interfaces.yang                 # -> ietf-interfaces_tree.txt
pyang -f tree ietf-interfaces.yang ietf-ip.yang    # -> ietf-interfaces+ip_tree.txt
```

- `ietf-interfaces` revisión 2018-02-20 (RFC 8343) e `ietf-ip` revisión 2018-02-22 (RFC 8344),
  tomados de los módulos que instala pyang 2.7.1 (`<python>/share/yang/modules/ietf/`).
- Leyenda: `rw` = configuración, `ro` = estado operativo, `*` = lista, `[name]` = llave de la lista,
  `?` = opcional, `{if-mib}?` = depende de una *feature*, `x` = obsoleto (deprecated).
- `interfaces-state` aparece como obsoleto en RFC 8343, pero IOS XE 17.12 lo sigue publicando y
  `monitorear_interfaces.py` lo usa para leer `oper-status`.
