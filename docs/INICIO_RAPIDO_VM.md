# Un maestro por VM Linux

Solo infraestructura operativa. No instala ni conecta el dashboard DPO.
Soporte de instalación: Ubuntu Server 24.04 LTS, usuario normal con sudo,
Python 3 preinstalado, Git y repositorio privado clonado. Linux de otras versiones
puede usar preparación/comprobación, pero debe instalar dependencias manualmente.

## 1. En cada VM

1. Instala Ubuntu y confirma IP, recursos, disco y acceso SSH según el plan real de red.
2. Instala Git si falta: `sudo apt-get update` y `sudo apt-get install -y git python3`.
3. Clona mediante autenticación privada de GitHub, sin escribir tokens en la URL:

```bash
git clone https://github.com/ElShapie/security-hub-infrastructure.git
cd security-hub-infrastructure
```

No vuelvas a clonar encima de un directorio existente. Para actualizar, revisa
`git status` y usa `git pull --ff-only` únicamente si no hay cambios locales.

## 2. VM-HUB-01

```bash
bash scripts/vm-hub.sh instalar
bash scripts/vm-hub.sh preparar
nano "$HOME/security-hub-runtime/hub/.env"
```

Completa OneLogin, DNS y confianza TLS siguiendo CONFIGURACION_MANUAL.md.
Docker requiere acceso al daemon. La instalación no agrega usuarios al grupo
docker: pertenecer a ese grupo equivale a privilegios de root. Si el administrador
lo autoriza, usa `sudo usermod -aG docker "$USER"`, cierra sesión y vuelve a entrar.
No ejecutes todo el maestro con sudo: crearía archivos privados para root.

```bash
bash scripts/vm-hub.sh comprobar
bash scripts/vm-hub.sh iniciar
bash scripts/vm-hub.sh estado
```

## 3. VM-NVR-01

```bash
bash scripts/vm-nvr.sh instalar
bash scripts/vm-nvr.sh preparar
nano "$HOME/security-hub-runtime/nvr/.env"
nano "$HOME/security-hub-runtime/nvr/config/config.yml"
```

Completa NVR_BIND_IP con la IP de ESTA VM, no la del Hub. Configura los streams
reales y contraseñas locales de cámaras. Revisa disco, certificados y firewall.

```bash
bash scripts/vm-nvr.sh comprobar
bash scripts/vm-nvr.sh iniciar
bash scripts/vm-nvr.sh estado
```

## 4. VM-RESPALDO-01

```bash
bash scripts/vm-respaldo.sh instalar
bash scripts/vm-respaldo.sh preparar
bash scripts/vm-respaldo.sh comprobar
```

Prepara carpetas privadas y herramientas age/OpenSSH. No crea cuentas compartidas,
no extrae datos de otras VM y NO instala una programación automática de copias.
Define claves, origen, destino, retención y restauración de ensayo en la guía manual.
`iniciar` solo verifica esta preparación; no inicia un servicio de backup.

## Qué hace y qué no hace

- `instalar`: instala dependencias del rol; Hub/NVR habilitan Docker. Requiere sudo.
- `preparar` (por defecto): copia únicamente el componente del rol a un runtime externo.
  Hub genera cuatro secretos independientes; NVR prepara config y carpetas.
- `comprobar`: revisa campos pendientes, permisos del .env y Compose sin imprimir secretos.
  NVR también revisa que su IP pertenezca a la VM.
- `iniciar`: arranque explícito con Docker Compose, nunca elimina volúmenes.
- `estado`: comprobación previa y consulta de Compose; no certifica salud de integraciones.
- `--runtime /ruta/dedicada`: destino alternativo fuera del repositorio.

No modifica IP, VLAN, firewall, hostname, OneLogin, tarjetas, cámaras ni base DPO.
No usa `docker compose down -v`, no restaura bases ni limpia datos.
No sobreescribe runtimes existentes: para actualizarlos hay que respaldar y revisar
el diff de código/Compose manualmente, preservando .env, config, datos y volúmenes.
Un runtime del preparador antiguo sin marcador se rechaza, no se adopta automáticamente.

## Verificación de aceptación

1. Hub: HTTPS válido, `/health`, login OneLogin, identidad SCIM EMP y permisos reales.
2. NVR: login con autenticación, cámara en vivo y grabación reproducible.
3. RFID: permitido y bloqueado con hardware identificado; nunca mostrar UID real.
4. SOC: evento observado y gestión de incidente autorizada.
5. Respaldo: copia cifrada, integridad y restauración en VM aislada.

La salida correcta del script no sustituye estas pruebas. Ver PRUEBA_INTEGRAL.md.
