# Servidores operativos virtuales

Esta plataforma está separada del dashboard DPO. El Security Hub maneja la operación del laboratorio; el dashboard DPO conserva únicamente cumplimiento, evidencias y seguimiento de privacidad.

Para ejecutar todo desde cero usa [Levantar las máquinas paso a paso](LEVANTAR_MAQUINAS_PASO_A_PASO.md). Para operar permisos, empleados y tarjetas usa [Guía de la interfaz](GUIA_INTERFAZ_SECURITY_HUB.md).

## Distribución recomendada

| Máquina virtual | Recursos mínimos | Servicios | Red |
|---|---:|---|---|
| `VM-HUB-01` | 2 vCPU, 4 GB RAM, 40 GB | Aplicación, SQLite, OneLogin OIDC, SCIM, API RFID | VLAN de servidores |
| `VM-NVR-01` | 4 vCPU, 8 GB RAM, 120 GB | Frigate y grabaciones de teléfonos | VLAN de cámaras y servidores |
| `VM-RESPALDO-01` | 2 vCPU, 2 GB RAM, 80 GB | Copias cifradas y restauración de ensayo | VLAN de administración |

Para la primera práctica pueden usarse dos VM: Hub y NVR. El respaldo puede ser una carpeta cifrada en otra laptop. No expongas SQLite, RTSP ni los puertos internos directamente a Internet.

## Preparar el Hub

En Ubuntu Server 24.04 o una versión LTS compatible:

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-v2 git
sudo usermod -aG docker "$USER"
```

Cierra sesión y vuelve a entrar para aplicar el grupo Docker. Después clona el repositorio privado y crea el runtime fuera del repositorio:

```bash
git clone https://github.com/ElShapie/security-hub-infrastructure.git
cd security-hub-infrastructure
python3 scripts/preparar_runtime.py --destino "$HOME/security-hub-runtime"
cd "$HOME/security-hub-runtime/hub"
```

Edita `.env` localmente. Completa `APP_BASE_URL`, `OIDC_CLIENT_ID`, `OIDC_CLIENT_SECRET` y `OIDC_METADATA_URL`. Los valores `APP_SECRET`, `SCIM_TOKEN` y `DEVICE_TOKEN` ya se generan de forma aleatoria. No copies `.env` al repositorio ni a evidencias.

La URL pública debe usar HTTPS. Para una práctica temporal puede utilizarse un túnel autenticado; para operación estable, configura un proxy inverso con certificado válido. En OneLogin registra exactamente:

```text
Redirect URI: https://DOMINIO_DEL_HUB/auth/callback
Login URL:    https://DOMINIO_DEL_HUB/login
SCIM Base:    https://DOMINIO_DEL_HUB/scim/v1
```

Inicia y comprueba:

```bash
docker compose up -d --build
docker compose ps
curl http://127.0.0.1:8000/health
docker compose logs --tail=100 app
```

El `health` local responde `{"status":"ok"}`. El navegador debe entrar por la URL HTTPS, nunca por el puerto interno.

## Preparar el NVR

En `VM-NVR-01`, copia el directorio `nvr` mediante el preparador o desde una copia revisada. Renombra `config.example.yml` a `config/config.yml`, completa las direcciones de los teléfonos y guarda las credenciales solo en `.env`.

```bash
cd "$HOME/security-hub-runtime/nvr"
mkdir -p config media certs
cp config.example.yml config/config.yml
docker compose up -d
docker compose ps
docker compose logs --tail=100 frigate
```

Empieza con dos teléfonos a 640×480 y 5 FPS. Confirma el consumo de CPU y disco antes de añadir cámaras. Conserva un día de grabación para la demostración y borra las grabaciones al terminar conforme al aviso de privacidad.

## Conectar el lector RFID

En la laptop conectada al lector instala `pyserial`, conserva el token únicamente como variable local y ejecuta:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install pyserial
export DEVICE_TOKEN='VALOR_DEL_ENV_DEL_HUB'
python registrar_tarjetas.py --puerto /dev/ttyACM0 \
  --servidor https://DOMINIO_DEL_HUB/api/v1/access-events \
  --lector PUERTA-PRINCIPAL
```

El programa guarda primero un CSV local y después intenta enviar el evento. Si el Hub no responde, el registro local permanece disponible. Usa identificadores de práctica, no nombres ni números reales de tarjeta.

## Qué ofrece esta primera versión

- Inicio de sesión obligatorio mediante OneLogin y aprovisionamiento SCIM.
- Permisos efectivos por número de empleado. TI los cambia gráficamente y el servidor los revalida en cada operación.
- Registro, vinculación, bloqueo y reactivación gráfica de tarjetas RFID/NFC por TI o Seguridad Física.
- Consola adaptable con métricas de identidades, servicios, accesos denegados e incidentes.
- Inventario de aplicación, base de datos, lectores, cámaras, NVR y red.
- API de entrada RFID protegida por un token distinto al de SCIM.
- Registro de incidentes del SOC y vistas de eventos de aplicación y acceso físico.
- Enlace al NVR sin incrustar credenciales ni video en la aplicación.
- Cookies seguras, CSRF en formularios, CSP, bloqueo de iframes y sesiones de 15 minutos.

## Límites actuales

SQLite es adecuado para 31 participantes y una demostración, pero no ofrece alta disponibilidad. La consola todavía no controla Frigate ni OneLogin: enlaza y recibe eventos, mientras esas plataformas conservan sus propios permisos. El estado de equipos se registra manualmente; una segunda etapa puede añadir comprobaciones periódicas. Antes de usar datos reales deben definirse retención, consentimiento para video, responsables y procedimiento de respaldo.
