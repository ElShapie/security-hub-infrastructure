"""Entradas Linux por VM: preparación conservadora, validación y arranque explícito."""
import argparse
import ipaddress
import json
import os
from pathlib import Path
import platform
import secrets
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def run(args, capture=False):
    result = subprocess.run(args, capture_output=capture, text=True, check=False)
    if result.returncode:
        # No reenviar stderr privado de Compose/FFmpeg ni configuración expandida.
        raise ValueError('Falló el comando ' + args[0] + '. Revise localmente; no publique logs sin sanitizar.')
    return result.stdout if capture else ''


def runtime_path(value):
    path = value.expanduser().absolute()
    if path.is_symlink() or any(p.is_symlink() for p in path.parents):
        raise ValueError('El runtime no puede atravesar enlaces simbólicos.')
    path = path.resolve()
    if path == Path.home().resolve() or path == Path(path.anchor) or path == ROOT or ROOT in path.parents:
        raise ValueError('Use una subcarpeta dedicada fuera del repositorio y distinta de HOME o raíz.')
    if path in ROOT.parents:
        raise ValueError('El runtime no puede contener el repositorio.')
    return path


def prepare(role, target):
    target.mkdir(parents=True, exist_ok=True, mode=0o700)
    dest = target / role
    if dest.is_symlink():
        raise ValueError('Destino con enlace simbólico no permitido.')
    if dest.exists():
        marker = dest / '.security-hub-runtime'
        if not marker.is_file() or marker.read_text().strip() != role:
            raise ValueError('Runtime preexistente no reconocido. Se conserva intacto; use otra carpeta o revise manualmente.')
        print('Runtime existente conservado: no se reemplazan código, secretos ni configuración.')
        return dest
    if role == 'respaldo':
        dest.mkdir(mode=0o700)
        for name in ('entradas', 'verificacion', 'restauracion-ensayo'):
            (dest / name).mkdir(mode=0o700)
    else:
        shutil.copytree(ROOT / role, dest, ignore=shutil.ignore_patterns('.env', 'data', 'media', 'certs', 'config', '__pycache__'))
        dest.chmod(0o700)
        content = (dest / '.env.example').read_text(encoding='utf-8')
        if role == 'hub':
            for placeholder in ('REEMPLAZAR_CON_SECRETO_GENERADO', 'REEMPLAZAR_CON_OTRO_SECRETO_GENERADO', 'REEMPLAZAR_CON_TOKEN_DE_DISPOSITIVOS', 'REEMPLAZAR_CON_SECRETO_PARA_TARJETAS'):
                content = content.replace(placeholder, secrets.token_urlsafe(48))
            content = content.replace('NVR_BASE_URL=https://REEMPLAZAR_HOST_NVR:8971', 'NVR_BASE_URL=')
        with (dest / '.env').open('x', encoding='utf-8') as file:
            file.write(content)
        (dest / '.env').chmod(0o600)
        if role == 'nvr':
            for name in ('config', 'media', 'certs'):
                (dest / name).mkdir(mode=0o700)
            shutil.copy2(dest / 'config.example.yml', dest / 'config/config.yml')
            (dest / 'config/config.yml').chmod(0o600)
    (dest / '.security-hub-runtime').write_text(role, encoding='utf-8')
    print('Runtime preparado fuera de Git. Consulte docs/CONFIGURACION_MANUAL.md antes de iniciar.')
    return dest


def env_values(dest):
    values = {}
    for line in (dest / '.env').read_text(encoding='utf-8').splitlines():
        if line.strip() and not line.lstrip().startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            values[key.strip()] = value.strip()
    return values


def validate(role, dest):
    if role == 'respaldo':
        if any(not (dest / name).is_dir() for name in ('entradas', 'verificacion', 'restauracion-ensayo')):
            raise ValueError('Prepare primero la VM de respaldo.')
        if not shutil.which('age') or not shutil.which('ssh'):
            raise ValueError('Faltan age/OpenSSH. Ejecute instalar y configure claves, cifrado y transferencia manualmente.')
        print('Directorios y herramientas disponibles. Esto NO confirma copias ni restauración.')
        return
    if not (dest / '.env').is_file():
        raise ValueError('Falta .env privado; ejecute preparar.')
    if os.name == 'posix' and ((dest / '.env').stat().st_mode & 0o077):
        raise ValueError('Ejecute chmod 600 sobre el .env privado.')
    values = env_values(dest)
    required = ('APP_SECRET', 'SCIM_TOKEN', 'DEVICE_TOKEN', 'CARD_PEPPER', 'HUB_HOST', 'APP_BASE_URL', 'OIDC_CLIENT_ID', 'OIDC_CLIENT_SECRET', 'OIDC_METADATA_URL') if role == 'hub' else ('NVR_BIND_IP', 'FRIGATE_CAM_ANDROID_USER', 'FRIGATE_CAM_ANDROID_PASSWORD', 'FRIGATE_CAM_IPHONE_USER', 'FRIGATE_CAM_IPHONE_PASSWORD')
    missing = [key for key in required if not values.get(key) or 'REEMPLAZAR' in values[key]]
    if missing:
        raise ValueError('Complete estos campos privados: ' + ', '.join(missing))
    if role == 'hub':
        if not values['APP_BASE_URL'].startswith('https://') or not values['OIDC_METADATA_URL'].startswith('https://'):
            raise ValueError('APP_BASE_URL y OIDC_METADATA_URL deben usar HTTPS.')
        credentials = [values[key] for key in required[:4]]
        if len(set(credentials)) != 4 or any(len(value) < 32 for value in credentials):
            raise ValueError('Los cuatro secretos locales deben ser distintos y de al menos 32 caracteres.')
    else:
        address = ipaddress.IPv4Address(values['NVR_BIND_IP'])
        if address.is_unspecified or address.is_loopback or address.is_multicast:
            raise ValueError('Use la IP concreta del NVR en la red del laboratorio.')
        addresses = json.loads(run(['ip', '-j', '-4', 'address', 'show'], capture=True))
        local = {entry['local'] for interface in addresses for entry in interface.get('addr_info', [])}
        if str(address) not in local:
            raise ValueError('NVR_BIND_IP no pertenece a esta VM. No se inicia Frigate.')
        config = dest / 'config/config.yml'
        if not config.is_file() or 'REEMPLAZAR' in config.read_text(encoding='utf-8'):
            raise ValueError('Complete config/config.yml con los streams reales antes de iniciar.')
    if not shutil.which('docker'):
        raise ValueError('Falta Docker. Ejecute instalar.')
    run(['docker', 'compose', 'version'], capture=True)
    run(['docker', 'info'], capture=True)
    run(['docker', 'compose', '--project-directory', str(dest), '-f', str(dest / 'compose.yml'), 'config', '--quiet'], capture=True)
    print('Validación previa correcta. OneLogin, cámaras y conectividad todavía requieren prueba real.')


def install(role):
    release = Path('/etc/os-release').read_text()
    if 'ID=ubuntu\n' not in release or 'VERSION_ID="24.04"' not in release:
        raise ValueError('Instalación automática soportada solo en Ubuntu Server 24.04. No se modifica esta distribución.')
    packages = ['python3', 'ca-certificates', 'curl', 'git', 'openssh-client', 'age']
    if role != 'respaldo':
        packages += ['docker.io', 'docker-compose-v2', 'iproute2']
    prefix = [] if os.geteuid() == 0 else ['sudo']
    run(prefix + ['apt-get', 'update'])
    run(prefix + ['apt-get', 'install', '-y'] + packages)
    if role != 'respaldo':
        run(prefix + ['systemctl', 'enable', '--now', 'docker'])
    print('Paquetes instalados. No se cambió red, firewall, grupos, hostname ni credenciales.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('vm', choices=('hub', 'nvr', 'respaldo'))
    parser.add_argument('accion', choices=('instalar', 'preparar', 'comprobar', 'iniciar', 'estado'), nargs='?', default='preparar')
    parser.add_argument('--runtime', type=Path, default=Path.home() / 'security-hub-runtime')
    args = parser.parse_args()
    try:
        if platform.system() != 'Linux':
            raise ValueError('Ejecute este maestro dentro de la VM Linux, no en Windows.')
        if args.accion == 'instalar':
            install(args.vm)
            return 0
        if os.geteuid() == 0:
            raise ValueError('Prepare y configure como usuario normal. Use sudo solo para instalar o para Docker si corresponde.')
        dest = runtime_path(args.runtime) / args.vm
        if args.accion == 'preparar':
            prepare(args.vm, dest.parent)
        else:
            validate(args.vm, dest)
            if args.vm != 'respaldo' and args.accion in ('iniciar', 'estado'):
                command = ['docker', 'compose', '--project-directory', str(dest), '-f', str(dest / 'compose.yml')]
                output = run(command + (['up', '-d', '--build'] if args.accion == 'iniciar' and args.vm == 'hub' else ['up', '-d'] if args.accion == 'iniciar' else ['ps']), capture=True)
                if args.accion == 'estado':
                    print(output)
                print('Orden ejecutada. Use el navegador y la prueba integral para confirmar salud y permisos.')
            elif args.vm == 'respaldo' and args.accion == 'iniciar':
                print('VM de respaldo lista para configuración manual. No se programan copias sin definir origen, claves y retención.')
        return 0
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(str(exc) if isinstance(exc, ValueError) else 'Error local de archivo/herramienta. Revise permisos y disponibilidad.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
