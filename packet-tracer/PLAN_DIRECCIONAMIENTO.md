# Plan de direccionamiento y puertos

## VLAN y redes

| VLAN | Nombre Cisco | Subred | Gateway | Uso |
|---:|---|---|---|---|
| 10 | `ADMIN` | `10.31.10.0/24` | `10.31.10.1` | TI, IAM, gestión y respaldo |
| 20 | `SERVERS` | `10.31.20.0/24` | `10.31.20.1` | Infraestructura, Hub y NVR |
| 30 | `USERS` | `10.31.30.0/24` | `10.31.30.1` | Dirección, RRHH, Seguridad Física y Auditoría |
| 40 | `CCTV_IOT` | `10.31.40.0/24` | `10.31.40.1` | Cámaras y RFID/NFC |
| 50 | `GUESTS` | `10.31.50.0/24` | `10.31.50.1` | Invitados aislados |
| 60 | `SOC` | `10.31.60.0/24` | `10.31.60.1` | Analistas SOC |
| 999 | `PARKING_NATIVE` | Sin DHCP | Sin gateway | Nativa y puertos sin uso |

## Direcciones estáticas

| Equipo | Dirección | Gateway | VLAN |
|---|---|---|---:|
| `SW-CORE-01` | `10.31.10.2` | `10.31.10.1` | 10 |
| `SW-ACCESS-01` | `10.31.10.3` | `10.31.10.1` | 10 |
| `VM-RESPALDO-01` | `10.31.10.22` | `10.31.10.1` | 10 |
| `SRV-INFRA-01` | `10.31.20.10` | `10.31.20.1` | 20 |
| `VM-HUB-01` | `10.31.20.20` | `10.31.20.1` | 20 |
| `VM-NVR-01` | `10.31.20.21` | `10.31.20.1` | 20 |
| `CAM-IP-01` | `10.31.40.31` | `10.31.40.1` | 40 |
| `CAM-IP-02` | `10.31.40.32` | `10.31.40.1` | 40 |
| `RFID-CTRL-01` | `10.31.40.40` | `10.31.40.1` | 40 |

DNS, NTP y Syslog apuntan a `10.31.20.10`. Los clientes usan DHCP desde `.100` hasta `.199` en cada red.

## Cableado propuesto

### SW-CORE-01

| Puerto | Modo | VLAN | Destino |
|---|---|---:|---|
| Gi0/1 | Trunk | 10,20,30,40,50,60; nativa 999 | RTR-HUB-01 Gi0/1 |
| Gi0/2 | Trunk | 10,20,30,40,50,60; nativa 999 | SW-ACCESS-01 Gi0/1 |
| Fa0/1 | Access | 20 | SRV-INFRA-01 |
| Fa0/2 | Access | 20 | VM-HUB-01 |
| Fa0/3 | Access | 20 | VM-NVR-01 |
| Fa0/4 | Access | 10 | VM-RESPALDO-01 |
| Fa0/5 | Trunk | 30,40,50,60; nativa 999 | AP-LAB-01 o WLC |
| Fa0/6–11 | Access | 10 | TI e IAM |
| Fa0/12–17 | Access | 60 | SOC |
| Fa0/18–24 | Parking | 999 | Apagados |

### SW-ACCESS-01

| Puerto | Modo | VLAN | Destino |
|---|---|---:|---|
| Gi0/1 | Trunk | 10,20,30,40,50,60; nativa 999 | SW-CORE-01 Gi0/2 |
| Fa0/1–18 | Access | 30 | Dirección, RRHH, Seguridad Física y Auditoría |
| Fa0/19 | Access | 40 | RFID-CTRL-01 |
| Fa0/20–24 | Parking | 999 | Apagados |

Los teléfonos-cámara se conectan por el SSID de VLAN 40. Si el AP simulado no admite VLAN por SSID, usa cuatro AP de Packet Tracer, uno por cada VLAN inalámbrica, y documenta que representan un único AP real con múltiples SSID.

