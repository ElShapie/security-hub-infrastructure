# Configuración manual y solución de problemas

Este documento complementa los maestros Linux. No contiene secretos ni datos reales.
No se integra con el dashboard DPO ni Supabase. Ejemplos de personas: EMP-001/EMP-002.
Los valores privados permanecen exclusivamente en el runtime fuera de Git.

## 1. Red y máquinas

1. Confirma interfaces con `ip -br address` y rutas con `ip route`.
2. Usa el PLAN_RED_Y_VLANS.md aprobado; la red plana de la guía antigua es solo ejemplo.
3. Reserva direcciones diferentes para Hub, NVR, respaldo y teléfonos.
4. Configura DNS para security-hub.lab y nvr.lab, o hosts local controlado.
5. Configura firewall del host y del hipervisor sin bloquear SSH. Docker puede publicar
   puertos fuera de las restricciones UFW: verifica reglas Docker/DOCKER-USER o ACL externas.
6. No publiques puertos en Internet ni abras 5000/1984 del NVR sin autenticación.

Los scripts no cambian red ni firewall: hacerlo sin conocer el equipo podría cortar SSH.

## 2. OneLogin: autenticación OIDC

1. En tu tenant, crea/configura una aplicación OpenID Connect para servidor web.
2. Registra la URL de inicio `https://security-hub.lab/login` y la callback exacta
   `https://security-hub.lab/auth/callback`. Si usas otro dominio, cambia ambos lados.
3. Permite flujo Authorization Code y scopes openid, profile, email según el conector.
4. Obtén client ID, client secret y URL de discovery del conector; no inventes el tenant
   ni publiques estos valores. Usa el endpoint de metadatos entregado por OneLogin.
5. En el .env privado del Hub completa OIDC_CLIENT_ID, OIDC_CLIENT_SECRET,
   OIDC_METADATA_URL, HUB_HOST y APP_BASE_URL (HTTPS).
6. Asigna usuarios autorizados a la aplicación. Sin asignación no basta tener una cuenta.
7. Ejecuta comprobar/iniciar y prueba login, logout, sesión y usuario desactivado.

OIDC autentica; SCIM aprovisiona; los permisos efectivos los controla el Hub.
El aviso visual "OneLogin activo" actual no es una prueba de conectividad.

## 3. OneLogin: aprovisionamiento SCIM

1. Usa el conector SCIM compatible con el endpoint existente `/scim/v1`.
   El Hub implementa SCIM Core 1.0: no asumir compatibilidad automática con conectores 2.0.
2. Base URL: `https://security-hub.lab/scim/v1`.
3. Configura autenticación Bearer con el SCIM_TOKEN del .env privado. Nunca copiar a Git.
4. Mapea userName según el conector, externalId al identificador EMP único,
   active al estado y title al rol inicial (por defecto consulta).
5. Prueba crear EMP-001, actualizar atributos y desactivar. Verifica respuesta del Hub
   y que una identidad desactivada no pueda entrar aunque conserve un rol local.
6. TI/admin asigna el rol efectivo autorizado desde Personas y tarjetas.

OneLogin debe alcanzar el endpoint por HTTPS confiable. Una VM con dominio .lab y
certificado local no es accesible ni confiable automáticamente desde el servicio cloud.
Coordina DNS/ruta y certificado público válido o un mecanismo privado aprobado;
no desactives validación TLS ni publiques el Hub sin controles para resolver SCIM.

## 4. HTTPS del Hub

1. Caddy actual usa `tls internal`: no equivale a certificado público confiable.
2. Después de iniciar, exporta SOLO el certificado raíz público:
   `docker compose cp caddy:/data/caddy/pki/authorities/local/root.crt ./security-hub-root.crt`
   desde el runtime hub. Nunca exportes la clave privada de la CA.
3. Instala la CA por canal controlado únicamente en equipos de laboratorio.
4. Confirma DNS, reloj y `curl https://security-hub.lab/health` sin ignorar TLS.
5. Si OneLogin cloud requiere acceso, configura certificado/ruta aprobados aparte.

## 5. Cámaras Android e iPhone

1. Elige una aplicación que realmente ofrezca RTSP o HTTP MJPEG en la red local.
   El sistema operativo del teléfono no determina un protocolo o ruta universal.
2. Activa cámara, permisos y una cuenta local exclusiva; no uses contraseñas personales.
3. Reserva IP y confirma puerto, ruta, protocolo y autenticación desde VM-NVR-01.
4. Prueba el stream en VLC localmente. No compartas URLs con contraseñas.
5. Edita config/config.yml privado: sustituye IP/ruta y el preset FFmpeg apropiado.
   El ejemplo Android MJPEG e iPhone RTSP NO demuestra compatibilidad con tu app.
6. Completa las variables FRIGATE_CAM_* en .env. Conserva referencias de variables
   en las URLs del YAML, no contraseñas literales.
7. El ejemplo exige dos cámaras configuradas. Para una sola, elimina el bloque
   no utilizado en el YAML privado; conserva los campos env exigidos por el maestro.
8. Empieza con resolución/FPS bajos; verifica carga, temperatura, batería y Wi-Fi.
9. Ejecuta comprobar/iniciar. Accede al puerto autenticado 8971 con TLS según configuración.
10. Recupera la credencial inicial de Frigate SOLO en logs locales, cámbiala y no publiques logs.
11. Confirma directo y grabación reproducible; después agrega la segunda cámara.

Frigate tiene autenticación propia. El enlace del Hub no implementa SSO OneLogin para NVR.
Certificados externos en certs y aceleración de video requieren configuración específica;
no montar GPU ni inventar dispositivos. Confirma requisitos de la versión fijada 0.17.1.

## 6. RFID/NFC

Identifica primero lector, microcontrolador, voltajes y pinout. Luego usa las guías
existentes rfid/ y prueba con identificadores ficticios. Configura DEVICE_TOKEN
solo en el dispositivo/servicio autorizado. No publicar UID, cableados inventados
ni secrets. Un script de VM no puede validar físicamente este circuito.

## 7. VM de respaldo

1. El maestro crea entradas, verificacion y restauracion-ensayo con permisos privados.
2. Define quién enviará y recibirá copias; configura claves SSH dedicadas y comprueba
   fingerprints por canal independiente. No desactives StrictHostKeyChecking.
   El maestro instala cliente SSH, no habilita un receptor SSH. Si las copias se envían
   hacia esta VM, instala `openssh-server` con autorización, crea una cuenta restringida
   y limita puerto 22 al origen aprobado. Alternativamente, esta VM puede extraer las
   copias mediante su cliente SSH sin abrir un servicio de recepción.
3. Genera una identidad age privada fuera de Git: `age-keygen -o /ruta/privada/backup.agekey`.
   Guarda copia offline de esa clave. Solo el destinatario público puede compartirse.
4. En Hub identifica el volumen real con Compose/Docker inspect; no adivines hub_app-data.
5. Reserva ventana de mantenimiento. Detén app mientras haces copia coherente de SQLite;
   garantiza reinicio incluso si copia/cifrado falla. Incluye .env y configuración privada
   únicamente en el backup CIFRADO, nunca en el repositorio.
6. Cifra usando `age -r DESTINATARIO_PUBLICO -o copia.tar.gz.age copia.tar.gz`.
   Comprueba retorno correcto antes de transferir y gestiona el temporal sin exposición.
7. Transfiere por SSH/SFTP a entradas. Calcula SHA-256 en origen y destino y compara.
8. Restaura y descifra SOLO en VM aislada, valida login/configuración/datos y documenta fecha.
9. Define retención y capacidad antes de automatizar con timer/cron. No borrar automáticamente
   la última copia sana. Videos NVR solo si el alcance y privacidad permiten respaldarlos.

No hay backup periódico instalado por estos maestros: falta definir cuentas, claves,
origen y política. Una copia con hash correcto no prueba que sea restaurable.

## 8. Fallos frecuentes y recuperación segura

| Síntoma | Comprobación / solución | Confirmación |
|---|---|---|
| python3 o git no existe | Instalar requisitos mínimos en Ubuntu antes del maestro | --help abre |
| Instalación rechaza sistema | Ver /etc/os-release; instalar manualmente si no es Ubuntu 24.04 | Docker y Compose disponibles |
| Permission denied Docker | Revisar daemon y autorización del usuario; no usar chmod 666 en socket | docker info funciona |
| Runtime existente rechazado | No borrar; respaldar y revisar carpeta; elegir otro --runtime | Preparación nueva sin tocar anterior |
| Campos REEMPLAZAR | Editar .env/config privados; nunca mostrarlos en capturas | comprobar pasa |
| cannot assign requested address | NVR_BIND_IP debe ser IP real de NVR, no Hub | ip -br address y comprobar |
| Puerto ocupado | Identificar proceso/contenedor; no matarlo ciegamente | Un único servicio en el puerto |
| Callback OneLogin inválida | Igualar dominio, HTTPS y /auth/callback en ambas configuraciones | Login completo |
| SCIM inaccesible o TLS inválido | Revisar accesibilidad cloud, DNS, CA y conector Core 1.0 | Crear/desactivar EMP de ensayo |
| Usuario sin permiso | Ver asignación OneLogin, active y rol efectivo | Prueba de rol permitido y denegado |
| Cámara negra / FFmpeg | Probar stream local, credenciales, ruta, preset, red y codec | Directo y grabación |
| No graba / disco lleno | Revisar df -h, permisos, retención; no borrar media indiscriminadamente | Grabación nueva reproducible |
| Error TLS | Corregir reloj, DNS y confianza/certificado; no usar -k como solución | HTTPS sin advertencias |
| Hub no saludable | Ver Compose ps y logs localmente; sanitizar antes de compartir | /health y login funcional |
| Copia o restauración falla | Conservar última copia válida; revisar cifrado/hash/espacio y origen | Restauración aislada exitosa |

## 9. Actualización y apagado

El maestro NO sincroniza código sobre un runtime existente. Antes de actualizar:
respaldo probado, revisión del diff, copia manual selectiva de código/Compose, sin
reemplazar secretos/config/datos. Reconstruye solo tras comprobar y conserva el volumen.
Para apagar, en el runtime usa `docker compose stop`; nunca `down -v` ni prune de volúmenes.
No ejecutar migraciones ni restauraciones de DPO: es otro proyecto.

## Fuentes oficiales consultadas

- https://developers.onelogin.com/docs/openid-connect/api/provider-config/
- https://developers.onelogin.com/docs/scim/create-app/
- https://docs.frigate.video/frigate/installation/
- https://docs.frigate.video/configuration/authentication/
- https://docs.frigate.video/configuration/config/

Revisión documental: 10 de octubre de 2026. Validación física y conexiones cloud pendientes.
