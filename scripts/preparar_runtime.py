"""Copy reviewed examples to a separate runtime and generate local secrets."""
import argparse
from pathlib import Path
import secrets
import shutil

ROOT = Path(__file__).resolve().parents[1]

def prepare(target):
    target = target.resolve()
    if target == ROOT or ROOT in target.parents:
        raise ValueError('Elegir una carpeta fuera del repositorio')
    for area in ['hub', 'nvr', 'rfid']:
        source = ROOT / area
        dest = target / area
        dest.mkdir(parents=True, exist_ok=True, mode=0o700)
        for p in source.iterdir():
            if p.is_file() and p.name != '.env':
                shutil.copy2(p, dest / p.name)
            elif p.is_dir() and p.name not in {'__pycache__', 'data'}:
                shutil.copytree(p, dest / p.name, dirs_exist_ok=True)
        env = dest / '.env'
        if area in ('hub', 'nvr') and not env.exists():
            content = (dest / '.env.example').read_text()
            if area == 'hub':
                content = content.replace('REEMPLAZAR_CON_SECRETO_GENERADO', secrets.token_urlsafe(48))
                content = content.replace('REEMPLAZAR_CON_OTRO_SECRETO_GENERADO', secrets.token_urlsafe(48))
                content = content.replace('REEMPLAZAR_CON_TOKEN_DE_DISPOSITIVOS', secrets.token_urlsafe(48))
                content = content.replace('REEMPLAZAR_CON_SECRETO_PARA_TARJETAS', secrets.token_urlsafe(48))
                content = content.replace('NVR_BASE_URL=https://REEMPLAZAR_HOST_NVR:8971', 'NVR_BASE_URL=')
            env.write_text(content)
            env.chmod(0o600)
    return target

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--destino', type=Path, default=Path.home() / 'security-hub-runtime')
    args = p.parse_args()
    try:
        prepare(args.destino)
        print('Runtime preparado. Completar los valores REEMPLAZAR en .env; secretos conservados localmente.')
    except ValueError as exc: p.error(str(exc))
