# Topología Cisco Packet Tracer

Esta carpeta contiene la topología lógica y las configuraciones listas para pegar en Cisco Packet Tracer. El diseño sigue el plan operativo del repositorio y no contiene nombres, credenciales ni datos reales.

## Equipos de la maqueta

| Equipo | Modelo en Packet Tracer | Función |
|---|---|---|
| `RTR-HUB-01` | Cisco 2911 | Inter-VLAN, DHCP, ACL y salida simulada |
| `SW-CORE-01` | Cisco 2960-24TT | Núcleo, servidores y estaciones administrativas |
| `SW-ACCESS-01` | Cisco 2960-24TT | Usuarios, SOC y controlador RFID |
| `SRV-INFRA-01` | Server-PT | DNS, NTP, Syslog y pruebas HTTP |
| `VM-HUB-01` | Server-PT | Security Hub y control de acceso |
| `VM-NVR-01` | Server-PT | Representación de Frigate NVR |
| `VM-RESPALDO-01` | Server-PT | Respaldo y administración |
| `AP-LAB-01` | AccessPoint-PT/WLC | SSID de usuarios, cámaras, invitados y SOC |
| `RFID-CTRL-01` | MCU/SBC-PT | Controlador RFID/NFC |
| `CAM-IP-01/02` | Webcam/IoT | Teléfonos usados como cámaras IP |

## Archivos

- [`TOPOLOGIA_PACKET_TRACER.md`](TOPOLOGIA_PACKET_TRACER.md): montaje completo y pruebas.
- [`PLAN_DIRECCIONAMIENTO.md`](PLAN_DIRECCIONAMIENTO.md): VLAN, IP, puertos y equipos.
- [`ACL_Y_FLUJOS.md`](ACL_Y_FLUJOS.md): política de comunicación.
- [`configs/RTR-HUB-01.txt`](configs/RTR-HUB-01.txt): router-on-a-stick, DHCP y ACL.
- [`configs/SW-CORE-01.txt`](configs/SW-CORE-01.txt): switch principal.
- [`configs/SW-ACCESS-01.txt`](configs/SW-ACCESS-01.txt): switch de acceso.
- [`topologia-security-hub.svg`](topologia-security-hub.svg): diagrama editable.
- [`topologia-security-hub.svg`](topologia-security-hub.svg): imagen vectorial para la presentación.

## Archivo `.pkt`

El formato `.pkt` es propietario y solo Cisco Packet Tracer puede crearlo de forma válida. Abre Packet Tracer, sigue la guía, pega las tres configuraciones y guarda el proyecto como `security-hub-topologia.pkt`. No renombres otro archivo a `.pkt` porque Packet Tracer lo considerará corrupto.
