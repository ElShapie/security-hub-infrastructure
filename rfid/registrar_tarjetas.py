"""Guarda lecturas RFID con hora UTC y local; E/S cambia el modo explícitamente."""
import argparse
import csv
import json
import os
import threading
from urllib.request import Request, urlopen
from datetime import datetime, timezone
from pathlib import Path
import serial

parser = argparse.ArgumentParser()
parser.add_argument('--puerto', required=True, help='Ejemplo: COM3 o /dev/ttyACM0')
parser.add_argument('--archivo', default='eventos_rfid.csv')
parser.add_argument('--servidor', help='Ejemplo: https://hub.example.test/api/v1/access-events')
parser.add_argument('--lector', default='LECTOR-01')
args = parser.parse_args()
port = serial.Serial(args.puerto, 9600, timeout=1)
path = Path(args.archivo)
new_file = not path.exists() or path.stat().st_size == 0

def commands():
    while True:
        try:
            command = input('E=entrada, S=salida: ').strip().upper()
            if command in ('E', 'S'):
                port.write(command.encode('ascii'))
                print('Modo solicitado:', 'ENTRADA' if command == 'E' else 'SALIDA')
        except EOFError:
            return

threading.Thread(target=commands, daemon=True).start()
try:
    with path.open('a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if new_file:
            writer.writerow(['hora_utc','hora_local','movimiento','uid','resultado','empleado'])
        while True:
            line = port.readline().decode('utf-8', errors='replace').strip()
            if not line:
                continue
            print(line)
            parts = line.split(',')
            if len(parts) != 4 or parts[0] not in ('ENTRADA', 'SALIDA') or parts[2] not in ('PERMITIDO','DENEGADO'):
                continue
            now = datetime.now(timezone.utc)
            writer.writerow([now.isoformat(), now.astimezone().isoformat(), *parts])
            f.flush()
            if args.servidor:
                token = os.environ.get('DEVICE_TOKEN', '')
                if len(token) < 32 or not args.servidor.startswith('https://'):
                    print('No se envió al hub: configura DEVICE_TOKEN y una URL HTTPS.')
                    continue
                body = json.dumps({'reader': args.lector, 'credential': parts[1],
                                   'movement': parts[0], 'result': parts[2],
                                   'reason': parts[3]}).encode('utf-8')
                try:
                    request = Request(args.servidor, data=body, method='POST', headers={
                        'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'})
                    with urlopen(request, timeout=5) as response:
                        print('Hub:', response.status)
                except Exception:
                    print('Hub no disponible; el evento permanece en el CSV local.')
except KeyboardInterrupt:
    print('\nRegistro terminado.')
finally:
    port.close()
