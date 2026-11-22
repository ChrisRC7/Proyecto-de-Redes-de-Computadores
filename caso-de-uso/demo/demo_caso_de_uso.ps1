<#
.SYNOPSIS
  Demo del caso de uso (CE-5301): configuracion y monitoreo de interfaces IOS XE por RESTCONF,
  alerta a Webex y ejemplo NETCONF. Pensado para grabar el video: cada paso muestra un titulo,
  el comando que se ejecuta y espera Enter antes de seguir.

.EXAMPLE
  .\demo\demo_caso_de_uso.ps1                 # demo completa, con pausas
  .\demo\demo_caso_de_uso.ps1 -Paso apagar    # solo un paso
  .\demo\demo_caso_de_uso.ps1 -SinPausa       # todo seguido
  .\demo\demo_caso_de_uso.ps1 -PausaSegundos 8  # avanza solo cada 8 s (para grabar)

  Requisitos: VPN del sandbox Catalyst 8000v conectada y caso-de-uso\.env completo.
#>
param(
    [ValidateSet('conectividad', 'crear', 'listar', 'modificar', 'monitorear', 'apagar', 'alerta',
                 'encender', 'borrar', 'netconf', 'yang')]
    [string[]]$Paso,
    [switch]$SinPausa,
    [int]$PausaSegundos = 0   # > 0: espera N segundos entre pasos en lugar de pedir Enter (grabación)
)

$ErrorActionPreference = 'Continue'
$env:PYTHONIOENCODING = 'utf-8'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Set-Location (Split-Path $PSScriptRoot -Parent)   # carpeta caso-de-uso

$loops = 'Loopback501', 'Loopback502', 'Loopback503'

$pasos = [ordered]@{
    conectividad = @{ Titulo = '1. Conectividad: GET a RESTCONF (ietf-interfaces)'
                      Cmd    = { python demo\conectividad.py } }
    crear        = @{ Titulo = '2. Configuracion: crear 3 loopbacks (PUT)'
                      Cmd    = { python configurar_interfaces.py crear } }
    listar       = @{ Titulo = '3. Verificar la configuracion creada (GET)'
                      Cmd    = { python configurar_interfaces.py listar } }
    modificar    = @{ Titulo = '4. Modificar la descripcion (PATCH)'
                      Cmd    = { python configurar_interfaces.py modificar --descripcion 'CE5301 - modificada por PATCH' } }
    monitorear   = @{ Titulo = '5. Monitoreo: estado operativo, todo arriba'
                      Cmd    = { python monitorear_interfaces.py --solo $loops --sin-webex } }
    apagar       = @{ Titulo = '6. Simular una falla: apagar Loopback502 (PATCH enabled=false)'
                      Cmd    = { python configurar_interfaces.py apagar --solo Loopback502 } }
    alerta       = @{ Titulo = '7. Monitoreo detecta la caida y envia la alerta a Webex'
                      Cmd    = { python monitorear_interfaces.py --solo $loops } }
    encender     = @{ Titulo = '8. Recuperar la interfaz (PATCH enabled=true)'
                      Cmd    = { python configurar_interfaces.py encender --solo Loopback502 } }
    borrar       = @{ Titulo = '9. Limpieza: borrar las loopbacks (DELETE)'
                      Cmd    = { python configurar_interfaces.py borrar } }
    netconf      = @{ Titulo = '10. NETCONF: sesion SSH 830 y RPC <get-config> (extracto)'
                      Cmd    = { python netconf_ejemplo.py | Select-Object -First 40 } }
    yang         = @{ Titulo = '11. Modelo YANG ietf-interfaces (pyang -f tree)'
                      Cmd    = { Get-Content yang\ietf-interfaces_tree.txt | Select-Object -First 40 } }
}

$elegidos = if ($Paso) { $Paso } else { $pasos.Keys }
foreach ($k in $elegidos) {
    $p = $pasos[$k]
    Write-Host ''
    Write-Host ('=' * 78) -ForegroundColor DarkCyan
    Write-Host "  $($p.Titulo)" -ForegroundColor Cyan
    Write-Host ('=' * 78) -ForegroundColor DarkCyan
    Write-Host ("PS> " + ($p.Cmd.ToString().Trim() -replace '\$loops', ($loops -join ' '))) -ForegroundColor Yellow
    & $p.Cmd
    if ($SinPausa -or $k -eq $elegidos[-1]) { continue }
    if ($PausaSegundos -gt 0) { Start-Sleep -Seconds $PausaSegundos; Clear-Host }
    else { Read-Host "`n[Enter] siguiente paso" | Out-Null; Clear-Host }
}
