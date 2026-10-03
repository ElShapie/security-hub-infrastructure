"""Datos y permisos de la aplicación de laboratorio."""
import json
import hashlib
import hmac
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

PERMISSIONS = {
    'admin': {'consulta', 'mantenimiento', 'admin', 'registros', 'hub', 'inventario', 'incidentes', 'usuarios', 'tarjetas'},
    'mantenimiento': {'consulta', 'mantenimiento'},
    'auditor': {'consulta', 'registros', 'hub'},
    'consulta': {'consulta'},
    'soc': {'consulta', 'registros', 'hub', 'incidentes'},
    'ti': {'consulta', 'mantenimiento', 'registros', 'hub', 'inventario', 'usuarios', 'tarjetas'},
    'seguridad_fisica': {'consulta', 'registros', 'hub', 'tarjetas'},
    'sin_acceso': set(),
}


def utc_now():
    return datetime.now(timezone.utc).isoformat()


class Store:
    def __init__(self, path):
        self.path = str(path)
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, username TEXT UNIQUE NOT NULL, payload TEXT NOT NULL, oidc_sub TEXT UNIQUE)')
            db.execute('CREATE TABLE IF NOT EXISTS events (time TEXT, user TEXT, action TEXT, result TEXT)')
            columns = {row['name'] for row in db.execute('PRAGMA table_info(events)')}
            if 'employee' not in columns:
                db.execute('ALTER TABLE events ADD COLUMN employee TEXT')
            db.execute('CREATE TABLE IF NOT EXISTS lab_state (key TEXT PRIMARY KEY, value TEXT NOT NULL)')
            db.execute("INSERT OR IGNORE INTO lab_state VALUES ('mode', 'ready')")
            db.execute("INSERT OR IGNORE INTO lab_state VALUES ('maintenance_runs', '0')")
            db.execute('''CREATE TABLE IF NOT EXISTS devices (
                id TEXT PRIMARY KEY, name TEXT NOT NULL, kind TEXT NOT NULL,
                address TEXT NOT NULL DEFAULT '', status TEXT NOT NULL,
                updated_at TEXT NOT NULL)''')
            db.execute('''CREATE TABLE IF NOT EXISTS access_events (
                id TEXT PRIMARY KEY, time TEXT NOT NULL, reader TEXT NOT NULL,
                credential TEXT NOT NULL, movement TEXT NOT NULL,
                result TEXT NOT NULL, reason TEXT NOT NULL DEFAULT '')''')
            db.execute('''CREATE TABLE IF NOT EXISTS incidents (
                id TEXT PRIMARY KEY, opened_at TEXT NOT NULL, title TEXT NOT NULL,
                severity TEXT NOT NULL, status TEXT NOT NULL,
                owner TEXT NOT NULL, summary TEXT NOT NULL DEFAULT '')''')
            db.execute('''CREATE TABLE IF NOT EXISTS role_overrides (
                user_id TEXT PRIMARY KEY, role TEXT NOT NULL, updated_at TEXT NOT NULL,
                updated_by TEXT NOT NULL)''')
            db.execute('''CREATE TABLE IF NOT EXISTS cards (
                id TEXT PRIMARY KEY, uid_hash TEXT UNIQUE NOT NULL, label TEXT NOT NULL,
                user_id TEXT NOT NULL, active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL, created_by TEXT NOT NULL)''')

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=15)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    def resource(self, row):
        return json.loads(row['payload']) if row else None

    def get(self, user_id):
        with self.connect() as db:
            return self.resource(db.execute('SELECT * FROM users WHERE id=?', (user_id,)).fetchone())

    def by_name(self, username):
        with self.connect() as db:
            return self.resource(db.execute('SELECT * FROM users WHERE username=?', (username.lower().strip(),)).fetchone())

    def all(self):
        with self.connect() as db:
            return [self.resource(r) for r in db.execute('SELECT * FROM users ORDER BY username')]

    def save(self, payload, user_id=None):
        if not isinstance(payload, dict):
            raise ValueError('El usuario debe ser un objeto JSON')
        previous = self.get(user_id) if user_id else None
        data = dict(previous or {})
        data.update(payload)
        username = str(data.get('userName', '')).strip().lower()
        if not username or '@' not in username:
            raise ValueError('userName debe ser un correo de laboratorio')
        active = data.get('active', True)
        if isinstance(active, str):
            if active.lower() not in ('true', 'false'):
                raise ValueError('active debe ser true o false')
            active = active.lower() == 'true'
        if not isinstance(active, bool):
            raise ValueError('active debe ser true o false')
        data['active'] = active
        data['userName'] = username
        data['id'] = user_id or str(uuid.uuid4())
        data.setdefault('schemas', ['urn:scim:schemas:core:1.0'])
        data['meta'] = {'resourceType': 'User', 'lastModified': utc_now()}
        with self.connect() as db:
            employee = str(data.get('externalId', '')).strip()
            if employee:
                duplicate = db.execute("SELECT id FROM users WHERE id!=? AND json_extract(payload,'$.externalId')=?", (data['id'], employee)).fetchone()
                if duplicate:
                    raise sqlite3.IntegrityError('Número de empleado duplicado')
            db.execute('INSERT INTO users(id,username,payload) VALUES(?,?,?) ON CONFLICT(id) DO UPDATE SET username=excluded.username,payload=excluded.payload', (data['id'], username, json.dumps(data)))
        self.event(data['id'], 'SCIM_CREATE' if previous is None else 'SCIM_UPDATE', 'OK')
        return data

    def remove(self, user_id):
        self.event(user_id, 'SCIM_DELETE', 'OK')
        with self.connect() as db:
            db.execute('UPDATE cards SET active=0 WHERE user_id=?', (user_id,))
            db.execute('DELETE FROM role_overrides WHERE user_id=?', (user_id,))
            db.execute('DELETE FROM users WHERE id=?', (user_id,))

    def bind_identity(self, user_id, subject):
        with self.connect() as db:
            row = db.execute('SELECT oidc_sub FROM users WHERE id=?', (user_id,)).fetchone()
            if row is None or (row['oidc_sub'] and row['oidc_sub'] != subject):
                return False
            try:
                db.execute('UPDATE users SET oidc_sub=? WHERE id=?', (subject, user_id))
            except sqlite3.IntegrityError:
                return False
        return True

    def permitted(self, user_id, action):
        user = self.get(user_id)
        return bool(user and user.get('active', False) and action in PERMISSIONS.get(self.effective_role(user_id), set()))

    def effective_role(self, user_id):
        with self.connect() as db:
            override = db.execute('SELECT role FROM role_overrides WHERE user_id=?', (user_id,)).fetchone()
        if override:
            return override['role']
        user = self.get(user_id)
        return str(user.get('title', 'sin_acceso')) if user else 'sin_acceso'

    def users_with_access(self):
        result = []
        for user in self.all():
            item = dict(user)
            item['effective_role'] = self.effective_role(user['id'])
            result.append(item)
        return result

    def set_role(self, user_id, role, actor):
        if role not in PERMISSIONS or not self.get(user_id):
            raise ValueError('Usuario o rol no válido')
        with self.connect() as db:
            db.execute('''INSERT INTO role_overrides(user_id,role,updated_at,updated_by) VALUES(?,?,?,?)
                ON CONFLICT(user_id) DO UPDATE SET role=excluded.role,updated_at=excluded.updated_at,updated_by=excluded.updated_by''',
                (user_id, role, utc_now(), actor))
        self.event(actor, 'ROLE_CHANGE:' + user_id, role)
        return role

    @staticmethod
    def card_fingerprint(uid, pepper):
        normalized = ''.join(c for c in str(uid).upper() if c in '0123456789ABCDEF')
        if len(normalized) < 4 or len(pepper) < 32:
            raise ValueError('UID o secreto no válido')
        digest = hmac.new(pepper.encode(), normalized.encode(), hashlib.sha256).hexdigest()
        return digest, digest[:12].upper()

    def add_card(self, payload, actor, pepper):
        uid_hash, fingerprint = self.card_fingerprint(payload.get('uid', ''), pepper)
        user_id = str(payload.get('user_id', ''))
        label = str(payload.get('label', '')).strip()[:60]
        user = self.get(user_id)
        if not user or not user.get('active', False) or not label:
            raise ValueError('Tarjeta o empleado no válido')
        item = {'id': str(uuid.uuid4()), 'uid_hash': uid_hash, 'label': label, 'user_id': user_id,
                'active': 1, 'created_at': utc_now(), 'created_by': actor}
        with self.connect() as db:
            db.execute('INSERT INTO cards VALUES(:id,:uid_hash,:label,:user_id,:active,:created_at,:created_by)', item)
        self.event(actor, 'CARD_LINK:' + user_id, fingerprint)
        return {**item, 'fingerprint': fingerprint}

    def cards(self):
        with self.connect() as db:
            rows = db.execute('''SELECT c.*, json_extract(u.payload,'$.externalId') employee
                FROM cards c LEFT JOIN users u ON u.id=c.user_id ORDER BY c.created_at DESC''')
            result = []
            for row in rows:
                item = dict(row)
                item['fingerprint'] = item.pop('uid_hash')[:12].upper()
                result.append(item)
            return result

    def set_card_active(self, card_id, active, actor):
        with self.connect() as db:
            changed = db.execute('UPDATE cards SET active=? WHERE id=?', (1 if active else 0, card_id)).rowcount
        if not changed:
            raise ValueError('Tarjeta no encontrada')
        self.event(actor, 'CARD_STATUS:' + card_id, 'ACTIVA' if active else 'BLOQUEADA')

    def check_card(self, uid, pepper):
        uid_hash, fingerprint = self.card_fingerprint(uid, pepper)
        with self.connect() as db:
            row = db.execute('''SELECT c.active card_active, c.label, u.payload
                FROM cards c LEFT JOIN users u ON u.id=c.user_id WHERE c.uid_hash=?''', (uid_hash,)).fetchone()
        if not row:
            return {'allowed': False, 'employee': None, 'label': fingerprint, 'reason': 'TARJETA_DESCONOCIDA'}
        user = json.loads(row['payload']) if row['payload'] else {}
        allowed = bool(row['card_active'] and user.get('active', False))
        return {'allowed': allowed, 'employee': user.get('externalId'), 'label': row['label'],
                'reason': 'AUTORIZADA' if allowed else 'TARJETA_O_EMPLEADO_INACTIVO'}

    def event(self, user, action, result):
        account = self.get(user)
        employee = str(account.get('externalId', user)) if account else user
        with self.connect() as db:
            db.execute('INSERT INTO events(time,user,action,result,employee) VALUES(?,?,?,?,?)', (utc_now(), user, action, result, employee))

    def events(self):
        with self.connect() as db:
            return [dict(r) for r in db.execute('SELECT * FROM events ORDER BY rowid DESC LIMIT 100')]

    def state(self):
        with self.connect() as db:
            return dict(db.execute('SELECT key,value FROM lab_state').fetchall())

    def maintain(self):
        with self.connect() as db:
            db.execute("UPDATE lab_state SET value=CAST(CAST(value AS INTEGER)+1 AS TEXT) WHERE key='maintenance_runs'")
            db.execute("INSERT INTO lab_state VALUES ('last_maintenance',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (utc_now(),))
        return self.state()

    def set_mode(self, mode):
        if mode not in ('ready', 'maintenance'):
            raise ValueError('Modo no válido')
        with self.connect() as db:
            db.execute("UPDATE lab_state SET value=? WHERE key='mode'", (mode,))
        return self.state()

    def dashboard(self):
        with self.connect() as db:
            return {
                'users_active': db.execute("SELECT COUNT(*) FROM users WHERE json_extract(payload,'$.active')=1").fetchone()[0],
                'devices_online': db.execute("SELECT COUNT(*) FROM devices WHERE status='online'").fetchone()[0],
                'devices_total': db.execute('SELECT COUNT(*) FROM devices').fetchone()[0],
                'denied_today': db.execute("SELECT COUNT(*) FROM access_events WHERE result='DENEGADO' AND date(time)=date('now')").fetchone()[0],
                'incidents_open': db.execute("SELECT COUNT(*) FROM incidents WHERE status!='cerrado'").fetchone()[0],
            }

    def save_device(self, payload):
        valid_kinds = {'aplicacion', 'base_datos', 'lector_rfid', 'camara', 'nvr', 'red'}
        valid_status = {'online', 'offline', 'mantenimiento'}
        name = str(payload.get('name', '')).strip()[:80]
        kind = str(payload.get('kind', '')).strip()
        status = str(payload.get('status', '')).strip()
        address = str(payload.get('address', '')).strip()[:120]
        if not name or kind not in valid_kinds or status not in valid_status:
            raise ValueError('Equipo no válido')
        item = {'id': str(payload.get('id') or uuid.uuid4()), 'name': name, 'kind': kind,
                'address': address, 'status': status, 'updated_at': utc_now()}
        with self.connect() as db:
            db.execute('''INSERT INTO devices(id,name,kind,address,status,updated_at) VALUES(:id,:name,:kind,:address,:status,:updated_at)
                ON CONFLICT(id) DO UPDATE SET name=excluded.name,kind=excluded.kind,address=excluded.address,status=excluded.status,updated_at=excluded.updated_at''', item)
        return item

    def devices(self):
        with self.connect() as db:
            return [dict(r) for r in db.execute('SELECT * FROM devices ORDER BY kind,name')]

    def add_access_event(self, payload):
        movement = str(payload.get('movement', '')).upper()
        result = str(payload.get('result', '')).upper()
        reader = str(payload.get('reader', '')).strip()[:80]
        credential = str(payload.get('credential', '')).strip()[:80]
        reason = str(payload.get('reason', '')).strip()[:160]
        if movement not in {'ENTRADA', 'SALIDA'} or result not in {'PERMITIDO', 'DENEGADO'} or not reader or not credential:
            raise ValueError('Evento de acceso no válido')
        item = {'id': str(uuid.uuid4()), 'time': utc_now(), 'reader': reader,
                'credential': credential, 'movement': movement, 'result': result, 'reason': reason}
        with self.connect() as db:
            db.execute('INSERT INTO access_events VALUES(:id,:time,:reader,:credential,:movement,:result,:reason)', item)
        return item

    def access_events(self, limit=100):
        with self.connect() as db:
            return [dict(r) for r in db.execute('SELECT * FROM access_events ORDER BY time DESC LIMIT ?', (min(max(int(limit), 1), 500),))]

    def add_incident(self, payload, owner):
        severity = str(payload.get('severity', '')).lower()
        title = str(payload.get('title', '')).strip()[:120]
        summary = str(payload.get('summary', '')).strip()[:1000]
        if severity not in {'baja', 'media', 'alta', 'critica'} or not title:
            raise ValueError('Incidente no válido')
        item = {'id': str(uuid.uuid4()), 'opened_at': utc_now(), 'title': title,
                'severity': severity, 'status': 'abierto', 'owner': owner, 'summary': summary}
        with self.connect() as db:
            db.execute('INSERT INTO incidents VALUES(:id,:opened_at,:title,:severity,:status,:owner,:summary)', item)
        return item

    def incidents(self):
        with self.connect() as db:
            return [dict(r) for r in db.execute('SELECT * FROM incidents ORDER BY opened_at DESC')]
