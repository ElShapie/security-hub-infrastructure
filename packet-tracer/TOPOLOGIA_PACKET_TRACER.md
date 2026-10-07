# Construcción de la topología en Cisco Packet Tracer

## 1. Crear el escenario

1. Abre Cisco Packet Tracer y crea un proyecto vacío.
2. Arrastra un router `2911` y nómbralo `RTR-HUB-01`.
3. Arrastra dos switches `2960-24TT` y nómbralos `SW-CORE-01` y `SW-ACCESS-01`.
4. Añade cuatro `Server-PT`: `SRV-INFRA-01`, `VM-HUB-01`, `VM-NVR-01` y `VM-RESPALDO-01`.
5. Añade un AP o WLC, dos cámaras IoT y un MCU/SBC para RFID.
6. Añade PCs representativas para TI, IAM, SOC, Dirección, RRHH, Seguridad Física y Auditoría. Usa identificadores `EMP`, nunca nombres reales.
7. Conecta con cable de cobre directo los equipos finales a los switches. Usa cobre directo para router-switch y un enlace Gigabit entre switches; Packet Tracer negocia automáticamente el tipo de cable en equipos recientes.

## 2. Conectar los enlaces principales

1. `RTR-HUB-01 Gi0/1` → `SW-CORE-01 Gi0/1`.
2. `SW-CORE-01 Gi0/2` → `SW-ACCESS-01 Gi0/1`.
3. Conecta servidores y estaciones según [`PLAN_DIRECCIONAMIENTO.md`](PLAN_DIRECCIONAMIENTO.md).
4. No añadas un segundo enlace entre switches.

## 3. Configurar los dispositivos Cisco

En cada dispositivo abre **CLI**, responde `no` al asistente inicial, entra a modo privilegiado con `enable` y luego a configuración con `configure terminal`.

Pega, en este orden:

1. [`configs/SW-CORE-01.txt`](configs/SW-CORE-01.txt) en el switch principal.
2. [`configs/SW-ACCESS-01.txt`](configs/SW-ACCESS-01.txt) en el switch de acceso.
3. [`configs/RTR-HUB-01.txt`](configs/RTR-HUB-01.txt) en el router.

Cuando Packet Tracer no acepte una línea de Syslog, NTP o seguridad por limitación del modelo, anota la línea como limitación y continúa; no elimines VLAN, trunks ni ACL.

## 4. Configurar servicios

### SRV-INFRA-01

1. En **Desktop > IP Configuration**, asigna `10.31.20.10/24`, gateway `10.31.20.1` y DNS `10.31.20.10`.
2. En **Services > DNS**, activa DNS y crea:
   - `security-hub.lab` → `10.31.20.20`
   - `nvr.lab` → `10.31.20.21`
3. Activa NTP y Syslog si la versión de Packet Tracer los ofrece.
4. Activa HTTP/HTTPS para usar el servidor como prueba controlada.

### VM-HUB-01 y VM-NVR-01

Configura `10.31.20.20/24` y `10.31.20.21/24`, respectivamente. Ambos usan gateway `10.31.20.1` y DNS `10.31.20.10`. Activa HTTPS. En la descripción del dispositivo indica que el primero representa Security Hub/OneLogin OIDC y el segundo Frigate NVR.

### Cámaras y RFID

Configura `CAM-IP-01` como `10.31.40.31`, `CAM-IP-02` como `10.31.40.32` y `RFID-CTRL-01` como `10.31.40.40`, máscara `/24`, gateway `10.31.40.1` y DNS `10.31.20.10`.

## 5. Configurar clientes

En cada PC entra a **Desktop > IP Configuration > DHCP**. Comprueba que TI/IAM recibe `10.31.10.x`, usuarios `10.31.30.x` y SOC `10.31.60.x`.

## 6. Pruebas mínimas

Ejecuta y registra el resultado:

| Origen | Prueba | Resultado esperado |
|---|---|---|
| TI | `ping 10.31.20.20` | Responde |
| TI | Navegar a `https://10.31.20.20` | Abre Hub simulado |
| Usuario | Navegar a `https://10.31.20.20` | Abre Hub simulado |
| Usuario | `ping 10.31.40.31` | Bloqueado |
| SOC | `ping 10.31.20.21` | Responde |
| SOC | `ping 10.31.40.31` | Responde para diagnóstico |
| Invitado | `ping 10.31.20.20` | Bloqueado |
| RFID | HTTPS a `10.31.20.20` | Permitido |
| RFID | `ping 10.31.30.100` | Bloqueado |

En los equipos Cisco captura también:

```text
show vlan brief
show interfaces trunk
show ip interface brief
show ip route
show access-lists
show port-security
show logging
show clock
```

## 7. Guardar

1. En cada dispositivo ejecuta `copy running-config startup-config`.
2. Selecciona **File > Save As**.
3. Guarda como `security-hub-topologia.pkt` junto a esta guía.
4. Cierra y vuelve a abrir el archivo para confirmar que no está corrupto.
5. Repite al menos una prueba permitida y una denegada.

