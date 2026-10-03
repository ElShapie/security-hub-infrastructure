"""Rechaza datos y archivos operativos antes de publicar."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SKIP = {'.git', '.venv', '__pycache__'}
FORBIDDEN_SUFFIXES = {'.db','.sqlite','.sqlite3','.xlsx','.xls','.zip','.pem','.key','.p12','.pfx','.mp4','.mkv','.avi','.jpg','.jpeg','.png','.log'}
PATTERNS = {
    'secreto de GitHub': re.compile(r'(?:gh[pousr]_[A-Za-z0-9]{25,}|github_pat_[A-Za-z0-9_]{30,})'),
    'clave privada': re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    'URL con credenciales': re.compile(r'(?:https?|rtsp)://[^\s/:{}]+:[^\s/@{}]+@'),
    'correo no ficticio': re.compile(r'[\w.+-]+@(?![\w.-]+\.(?:test|example)\b)[A-Za-z0-9.-]+\.[A-Za-z]{2,}'),
}

def main():
    problems = []
    for path in ROOT.rglob('*'):
        if not path.is_file() or set(path.relative_to(ROOT).parts) & SKIP:
            continue
        if path.name.startswith('.env') and path.name != '.env.example':
            problems.append(f'{path.relative_to(ROOT)}: configuración privada')
            continue
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            problems.append(f'{path.relative_to(ROOT)}: archivo operativo no permitido')
            continue
        try:
            text = path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            problems.append(f'{path.relative_to(ROOT)}: archivo binario no revisado')
            continue
        for label, pattern in PATTERNS.items():
            if pattern.search(text):
                problems.append(f'{path.relative_to(ROOT)}: {label}')
    if problems:
        print('\n'.join(problems))
        return 1
    print('Repositorio revisado sin datos operativos ni secretos detectados.')
    return 0

if __name__ == '__main__':
    sys.exit(main())
